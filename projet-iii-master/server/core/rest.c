/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 */

#include <limits.h>
#include <errno.h>
#include <unistd.h>

#include "core/io.h"
#include "core/rest.h"
#include "utils/btree.h"
#include "utils/hash.h"
#include "utils/http.h"

static struct btree *rest_interface_table;

void rest_register(struct rest_interface *interface)
{
	u64 hash;

	if (!interface->route) {
		warning("rest: Trying to register NULL route");
		return;
	}

	hash = hash_djb2(interface->route, NULL);

	btree_kinit(hash, &interface->node);

	if (btree_add(&interface->node, &rest_interface_table) < 0) {
		warning("rest: Route %s already exists!", interface->route);
	}
}

static void send_response(FILE *fp, enum http_status status, struct json *response)
{
	info("sending response ...");

	if (!response) {

		fprintf(fp,
			"HTTP/1.1 %d %s\r\n"
			"Content-Length: 2\r\n"
			"\r\n"
			"{}",
			status, http_status_string(status));
		goto done;
	}

#ifdef CONFIG_TRANSFERT_ENCODING_CHUNKED
	debug("transfert chunk");
	fprintf(fp,
		"HTTP/1.1 %d %s\r\n"
		"Content-Type: application/json\r\n"
		"Transfer-Encoding: chunked\r\n"
		"\r\n",
		status, http_status_string(status));
	json_stream_http(response, fp);
#else
	{
		char *buf;
		usize buf_size;
		FILE *buf_fp;

		buf_fp = open_memstream(&buf, &buf_size);

		json_stream(response, buf_fp);

		fflush(buf_fp);

		fprintf(fp,
			"HTTP/1.1 %d %s\r\n"
			"Content-Type: application/json\r\n"
			"Content-Length: %zu\r\n"
			"\r\n"
			"%s",
			status, http_status_string(status),
			buf_size, buf);

		fclose(buf_fp);
		free(buf);
	}
#endif
done:
	fflush(fp);
	info("Reponse %d", status);
}

static bool dispatch_method(FILE *rd, FILE *wr, const char *user, struct http_request *req,
			enum http_status (*method)(const char *user, const struct json *, struct json **))
{
	struct json *request, *response;
	enum http_status status;

	{
		usize len;

		len      = req->content_length;
		request	 = NULL;

		if (len) {
			int err;

			info("parsing body");
			err = json_parse(rd, &request);
			info("body parsed");

			if (err) {
				warning("bad body of request");
				send_response(wr, HTTP_BAD_REQUEST, NULL);
				return false;
			}

			{
				char *tmp = json_stringify2(request);
				debug("body => %s", tmp);
				free(tmp);
			}
		}
	}

	response = NULL;

	info("calling route's method");

	status = method(user, request, &response);

	send_response(wr, status, response);

	if (request) {
		json_destroy(request);
	}

	if (response) {
		json_destroy(response);
	}

	return true;
}

static bool handle_request(FILE *rd, FILE *wr, struct http_request *req)
{
	struct rest_interface *interface;
	struct btree *interface_node;
	enum http_status (*method)(const char *, const struct json *, struct json **);
	bool requires_auth;

	interface_node = btree_find(hash_djb2(req->URI, NULL), rest_interface_table);

	if (!interface_node) {
		warning("invalid route %s", req->URI);
		send_response(wr, HTTP_NOT_FOUND, NULL);
		return false;
	}

	interface = container_of(interface_node, struct rest_interface, node);

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wswitch-enum"
	switch (req->method) {

	case HTTP_GET:
		method	      = interface->get;
		requires_auth = interface->options & REST_AUTH_GET;
		break;

	case HTTP_PUT:
		method	      = interface->put;
		requires_auth = interface->options & REST_AUTH_PUT;
		break;

	case HTTP_POST:
		method	      = interface->post;
		requires_auth = interface->options & REST_AUTH_POST;
		break;

	default:
		method = NULL;
		requires_auth = false;
	}
#pragma GCC diagnostic pop

	if (!method) {
		warning("invalid method for route");
		send_response(wr, HTTP_METHOD_NOT_ALLOWED, NULL);
		return false;
	}

	{
		char *user;
		bool ret;

		if (requires_auth) {
			enum http_status status;

			status = http_auth(req, &user);

			if (HTTP_OK != status) {
				warning("fail to authentify %s", user);
				send_response(wr, status, NULL);
				ret = false;
				goto bad_auth;
			}

			info("authentication success!");
		} else {
			user = NULL;
		}

		ret = dispatch_method(rd, wr, user, req, method);
	bad_auth:
		if (user) {
			free(user);
		}

		return ret;
	}
}

/*
 * Set to true if server should handle keep-alive HTTP connections.
 */
#define HANDLE_KEEP_ALIVE true

void rest_handle(FILE *rd, FILE *wr)
{
	do {

		struct http_request req __attribute__((cleanup(http_clean))) = { 0 };

		int err;

		info("scanning request ..");
		err = http_scan(&req, rd);
		info("request scanned");

		/* EOF */
		if (0 == err) {
			break;
		}

		if (err < 0 || unlikely(!req.URI)) {
			warning("bad request");
			send_response(wr, HTTP_BAD_REQUEST, NULL);
			break;
		}

		info("handling request..");

		if (!handle_request(rd, wr, &req)) {
			break;
		}

	} while(HANDLE_KEEP_ALIVE);
}

/* gf: rest_register_lib_ctor */
REST_REGISTER_LIB;
