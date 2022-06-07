/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 */

#include <arpa/inet.h>
#include <errno.h>
#include <netdb.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#include <openssl/err.h>
#include <openssl/ssl.h>

#include "core/auth.h"
#include "core/io.h"
#include "core/rest.h"
#include "core/poll.h"
#include "utils/opt.h"

/* For CLI options parsing */
extern struct opt OPT_BEG_SECTION;
extern struct opt OPT_END_SECTION;

/* Program informations */
static const char program_name[]	= "bixi-server";
static const char program_usage[]	= "Usage: bixi-server [options]";
static const uint program_major_version = 2;
static const uint program_minor_version = 0;
static const uint program_patch_version = 0;

static bool disable_tls = false;
OPT_MAKE_FLG("no-tls", "Use HTTP instead of HTTPS", &disable_tls);

static const char *tls_cert = NULL;
OPT_MAKE_STR("cert", "Certificate to use with TLS", &tls_cert);

static const char *tls_key = NULL;
OPT_MAKE_STR("key", "Private key to use with TLS", &tls_key);

static int port = 443;
OPT_MAKE_INT("port", "Set the port to use (default to 443)", &port);

static bool allow_any_addr = false;
OPT_MAKE_FLG("no-loop", "Setup connection to none loopback address", &allow_any_addr);

static const char *working_directory = NULL;
OPT_MAKE_STR("wd", "Set working directory", &working_directory);

static void print_version(void)
{
	printf("%s version %u.%u.%u\n",
	       program_name, program_major_version,
	       program_minor_version, program_patch_version);

	exit(EXIT_SUCCESS);
}
OPT_MAKE_CLB("version", "Print software version", &print_version);

static void print_help(void)
{
	opt_usage(program_usage, &OPT_BEG_SECTION,
		  &OPT_END_SECTION - &OPT_BEG_SECTION);

	exit(EXIT_SUCCESS);
}
OPT_MAKE_CLB("help", "Print this message", &print_help);


static u64 client_ID = 0;

static ssize_t ssl_read_wrapper(void *cookie, char *buf, size_t size)
{
	size_t readbytes;
	int err;

	err = SSL_read_ex(cookie, buf, size, &readbytes);

	if (1 == err) {
		return readbytes;
	}

	err = SSL_get_error(cookie, err);

	switch (err) {
	case SSL_ERROR_ZERO_RETURN:
		return 0;
	}

	return -1;
}

static ssize_t ssl_write_wrapper(void *cookie, const char *buf, size_t size)
{
	int err;
	size_t	written;

	err = SSL_write_ex(cookie, buf, size, &written);

	if (1 == err) {
		return written;
	}

	return 0;
}

static int ssl_close_wrapper(void *cookie)
{
	BIO_flush(SSL_get_rbio(cookie));
	SSL_free(cookie);
	return 0;
}

/*
 * glibc extension; Wrappers for SSL streaming of socket.  This allows
 * us to use one data structure for all communication, encrypted or
 * not.
 *
 * Note: You can't seek a stream, thus NULL.
 */
static const cookie_io_functions_t ssl_function_table = {
	.read  = ssl_read_wrapper,
	.write = ssl_write_wrapper,
	.seek  = NULL,
	.close = ssl_close_wrapper
};

static void client_set_log(int client)
{
	struct sockaddr addr;
	struct sockaddr_in addr_in;
	socklen_t addr_len;
	char *ident;
	size_t ident_len;

	/* If fail */
	char host[INET_ADDRSTRLEN] = "???";

	addr_len = sizeof(addr);

	if (0 == getpeername(client, &addr, &addr_len)) {
		memcpy(&addr_in, &addr, sizeof(addr_in));
		inet_ntop(AF_INET, &addr_in.sin_addr, host, sizeof(host));
	}

	/*  1 space + 2 square brackets + 1 @ + 1 end of string + 21 for max u64 */
	ident_len = strlen(program_name) + strlen(host) + 5 + 21;
	ident	  = malloc(ident_len);

	snprintf(ident, ident_len, "%s [%" PRIu64 "@%s]", program_name, client_ID, host);

	openlog(ident,
		LOG_NDELAY | LOG_NOWAIT | LOG_PERROR,
		LOG_DAEMON);
}

#define GET_OPENSSL_ERR "TODO"

/*
 * Serve client with REST API.	TLS is supported by default.  See CLI
 * -no-tls to deactivate encryption of client communications,
 * i.e. HTTP instead of HTTPS.
 */
static void serve_client(int client, SSL_CTX *openssl_context)
{
	int err;
	SSL *ssl;
	FILE *rd, *wr;

	client_set_log(client);

	info("connection accepted");

	if (disable_tls) {
		rd  = fdopen(client, "rb");
		wr  = fdopen(dup(client), "wb");
		goto no_tls;
	}

	ssl = SSL_new(openssl_context);

	if (!ssl) {
		critical("can't create SSL state - %s", GET_OPENSSL_ERR);
		goto bad_ssl;
	}

	if (0 == SSL_set_fd(ssl, client)) {
		critical("can't set file descriptor for SSL - %s", GET_OPENSSL_ERR);
		goto bad_fd;
	}

	err = SSL_accept(ssl);

	if (err != 1) {
		critical("can't complete TLS handshake - %s",
			 ERR_error_string(SSL_get_error(ssl, err), NULL));
		SSL_free(ssl);
		goto bad_handshake;
	}

	info("TLS handshake successful");

	/*
	 * Since we're opening 2 streams, we need to increment the
	 * reference count of the SSL object by one
	 */
	SSL_up_ref(ssl);
	rd = fopencookie(ssl, "rb", ssl_function_table);
	wr = fopencookie(ssl, "wb", ssl_function_table);


no_tls:
	if (!rd || !wr) {
		critical("fail to create file cookie for SSL - %m");
		goto bad_file;
	}

	rest_handle(rd, wr);
	info("bye bye");

	/*
	 * This is actually useless since all of this will be close
	 * upon process termination by the Kernel.  But we're doing
	 * either way if one day we decide to use threads instead of
	 * processes.
	 */
bad_file:
	if (rd || wr) {
		fclose(rd);
		fclose(wr);
	}
bad_handshake:
bad_fd:
bad_ssl:
	shutdown(client, SHUT_RDWR);

	/* Make ASAN quiet */
#ifdef CONFIG_ASAN
	SSL_CTX_free(openssl_context);
#endif
}

static void on_sigterm(int sig)
{
	(void)sig;

	info("SIGTERM");
	exit(EXIT_SUCCESS);
}

__noreturn
static void serve_forever(int server, SSL_CTX *openssl_context)
{
	if (working_directory) {
		if (chdir(working_directory) < 0) {
			panic("can't set wd %s: %m", working_directory);
		}
	}

	/* Setting up data base */
	{
		auth_init();
	}

	/* Setting up signal handlers */
	{
		signal(SIGCHLD, SIG_IGN);
		signal(SIGTERM, on_sigterm);
	}


	while (true){

		int client;

		/* accept4 nonstadard Linux extension */
		client = accept4(server, NULL, NULL, SOCK_CLOEXEC);

		++client_ID;

		if (unlikely(client) < 0) {
			warning("fail to accept connection: %m");
		}

		switch (fork()) {
		case -1:
			critical("can't serve client - fork(): %m");
			break;
		case 0:
			/* Don't keep reference to the server socket! */
			close(server);
			serve_client(client, openssl_context);
			exit(EXIT_SUCCESS);
			break;
		}

		/* Child is the owner of the cloned socket */
		close(client);
	}
}

int main(int argc, char *argv[])
{
	/* Setting up logging */
	{
		openlog(program_name,
			LOG_NDELAY | LOG_NOWAIT | LOG_PERROR,
			LOG_DAEMON);
	}

	/* Parsing command line options */
	{
		argc = opt_parse(argc, argv, &OPT_BEG_SECTION,
				 &OPT_END_SECTION - &OPT_BEG_SECTION);

		if (argc < 0) {
			opt_usage(program_usage, &OPT_BEG_SECTION,
				  &OPT_END_SECTION - &OPT_BEG_SECTION);
			exit(EXIT_FAILURE);
		}

		if (port < 0) {
			panic("port must be a positive integer");
		}
	}

	/* Make server */
	{
		int server;
		SSL_CTX *openssl_context;

		openssl_context = NULL;

		/* Setting up OpenSSL context */
		if (!disable_tls) {

			int err;

			SSL_load_error_strings();
			OpenSSL_add_ssl_algorithms();

			if (!tls_cert) {
				panic("Missing certificate for TLS");
			}

			if (!tls_key) {
				panic("Missing private key for TLS");
			}

			openssl_context = SSL_CTX_new(TLS_method());

			if (!openssl_context) {
				panic("can't create OpenSSL context - %s",
				      GET_OPENSSL_ERR);
			}

			SSL_CTX_set_ecdh_auto(openssl_context, 1);

			err = SSL_CTX_use_certificate_file(openssl_context,
							   tls_cert,
							   SSL_FILETYPE_PEM);
			if (err <= 0) {
				ERR_print_errors_fp(stderr);
				exit(EXIT_FAILURE);
			}

			err = SSL_CTX_use_PrivateKey_file(openssl_context,
							  tls_key,
							  SSL_FILETYPE_PEM);
			if (err <= 0 ) {
				ERR_print_errors_fp(stderr);
				exit(EXIT_FAILURE);
			}
		}

		/* protocol is always 0 */
		server = socket(AF_INET, SOCK_STREAM, 0);

		if (server < 0) {
			panic("can't create socket for server: %m");
		}

		/* Bind to either any address localy or only loopback */
		{
			struct sockaddr_in addr;

			memset(&addr, '\0', sizeof(addr));

			addr.sin_family = AF_INET;
			addr.sin_port	= htons((u16)port);

			if (allow_any_addr) {
				addr.sin_addr.s_addr = htonl(INADDR_ANY);
			} else {
				addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
			}

			/* Allow reeuse of address:port for same effective UID */
			setsockopt(server, SOL_SOCKET, SO_REUSEPORT, &(int[]){1}, sizeof(int));

			if (bind(server, (const struct sockaddr*)&addr, sizeof(addr)) < 0) {
				panic("can't bind server to %s:%d - %m",
				      inet_ntoa(addr.sin_addr), port);
			}

			if (listen(server, 0) < 0) {
				panic("server can't listen: %m");
			}

			info("listening at https://%s:%d", inet_ntoa(addr.sin_addr), port);
		}

		serve_forever(server, openssl_context);
	}
}
