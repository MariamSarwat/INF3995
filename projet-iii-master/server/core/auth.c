/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 */

#include <fcntl.h>
#include <string.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#include "core/auth.h"
#include "core/io.h"

static int auth_fd = -1;

void auth_init(void)
{
	mkdir("auth", 0700);

	auth_fd = open("auth", O_CLOEXEC | O_DIRECTORY, 0700);

	if (auth_fd < 0) {
		panic("can't open authentication directory - %m");
	}
}

bool auth_authenticate(const char *restrict user, const char *restrict passwd)
{
	int fd;
	usize passwd_len;
	bool granted;

	granted = false;

	fd = openat(auth_fd, user, O_RDONLY);

	if (fd < 0) {
		warning("auth: User '%s' doesn't exist", user);
		goto bad_user;
	}

	passwd_len = strlen(passwd);

	flock(fd, LOCK_SH);
	{
		struct stat statbuf;
		char *real_passwd;
		usize left;

		fstat(fd, &statbuf);

		if ((usize)statbuf.st_size != passwd_len) {
			goto bad_passwd_len;
		}

		real_passwd = malloc(passwd_len);
		left	    = passwd_len;

		while (left) {
			isize rd;

			rd = read(fd, real_passwd, left);

			if (unlikely(rd < 0)) {
				critical("fail to read user %s passwd - %m", user);
				goto bad_read;
			}

			if (0 == strncmp(real_passwd, passwd, rd)) {
				passwd += rd;
				left   -= rd;
			} else {
				goto bad_passwd;
			}

		}

		granted = true;

	bad_passwd:
	bad_read:
		flock(fd, LOCK_UN);
		explicit_bzero(real_passwd, passwd_len);
		free(real_passwd);
	}
bad_passwd_len:
	close(fd);		/* Implicit unlock! */

bad_user:
	return granted;
}

int auth_change(const char *restrict user, const char *restrict new_passwd)
{
	usize passwd_len;
	int ret, fd;

	ret = -1;

	passwd_len = strlen(new_passwd);

	if (0 == passwd_len) {
		goto bad_passwd;
	}

	fd = openat(auth_fd, user, O_WRONLY | O_CREAT | O_TRUNC);

	if (fd < 0) {
		warning("can't set user '%s' passwd - %m", user);
		goto bad_fd;
	}

	/* TODO:old - Do atomic update using rename(2) */
	flock(fd, LOCK_EX);
	{
		ftruncate(fd, passwd_len);

		do {
			isize wr;

			wr = write(fd, new_passwd, passwd_len);

			if (wr < 0) {
				warning("fail to update passwd for user %s - %m", user);
				break;
			} else {
				passwd_len -= wr;
				new_passwd += wr;
			}

		} while(passwd_len);

		ret = 0;
	}
	close(fd);		/* Implicit unlock! */
bad_fd:
bad_passwd:
	return ret;
}
