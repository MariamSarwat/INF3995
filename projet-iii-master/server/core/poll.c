/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 */

#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#include "core/io.h"
#include "utils/json.h"

__pure
static bool sanitize_email(const char *email)
{
	char c;

	if (email[0] == '\0') {
		return false;
	}

	while ((c = *(email++)) != '\0') {
		if (unlikely(c == '/')) {
			return false;
		}
	}

	return true;
}

int poll_put(const struct json *info)
{
	const struct json  *j_email, *firstname, *lastname, *age, *interest;
	const char *email;
	int err;
	int fd;
	int poll_dfd;

	poll_dfd = open("poll", O_CLOEXEC | O_DIRECTORY);

	if (poll_dfd < 0) {
		critical("can't open poll directory - %m");
		return -2;
	}

	err = -1;

	j_email = json_dict_get(info, "courriel");

	if (!j_email || !json_is_string(j_email) || !sanitize_email(json_to_string(j_email))) {
		goto bad_email;
	}

	email = json_to_string(j_email);

	firstname = json_dict_get(info, "prenom");

	if (!firstname || !json_is_string(firstname)) {
		goto bad_firstname;
	}

	lastname = json_dict_get(info, "nom");

	if (!lastname || !json_is_string(lastname)) {
		goto bad_lastname;
	}

	age = json_dict_get(info, "age");

	if (!age || !json_is_number(age) || json_to_number(age) <= 0) {
		goto bad_age;
	}

	interest = json_dict_get(info, "interet");

	if (!interest || !json_is_boolean(interest)) {
		goto bad_interest;
	}

	fd = openat(poll_dfd, email, O_WRONLY | O_CREAT, 0600);

	if (fd < 0) {
		warning("can't open poll of '%s' - %m", email);
		goto bad_fd;
	}

	if (flock(fd, LOCK_EX) < 0) {
		warning("fail to get exclusive lock for '%s' - %m", email);
		goto bad_lock;
	} else {

		if (json_streamfd(info, fd) < 0) {
			warning("fail to write to file for '%s' - %m", email);
		}

		flock(fd, LOCK_UN);
	}
bad_lock:
	close(fd);

	err = 0;

bad_fd:
bad_interest:
bad_age:
bad_lastname:
bad_firstname:
bad_email:

	return err;
}

long int poll_get(struct json **pinfos)
{
	struct json *infos;
	isize cnt;
	DIR *dirp;
	int poll_dfd;

	poll_dfd = open("poll", O_CLOEXEC | O_DIRECTORY);

	if (poll_dfd < 0) {
		critical("can't open poll directory - %m");
		return -2;
	}

	dirp = fdopendir(poll_dfd);

	if (!dirp) {
		error("can't fdopendir() on poll directory - %m");
		return -1;
	}

	infos = json_array();
	cnt   = 0;

	errno = 0;
	for (struct dirent *entry=readdir(dirp); entry; entry=readdir(dirp)) {

		int fd;

		/*
		 * This directory is supposed to be filled only with
		 * regular files
		 */
		if (unlikely(DT_REG != entry->d_type)){
			continue;
		}

		fd = openat(poll_dfd, entry->d_name, O_RDONLY);

		if (fd < 0) {
			warning("can't open poll file %s - %m", entry->d_name);
			continue;
		}

		{
			struct json *info;
			FILE *fp;

			if (flock(fd, LOCK_SH) < 0) {
				warning("fail to lock poll file '%s'", entry->d_name);
				goto bad_lock;
			}

			fp = fdopen(dup(fd), "rb");

			if (unlikely(!fp)) {
				warning("fail to open filestream on '%s'", entry->d_name);
				goto bad_fp;
			}

			if (0 == json_parse(fp, &info)) {
				json_array_push(infos, info);
				++cnt;
			}

			fclose(fp);
		bad_fp:
			flock(fd, LOCK_UN);
		bad_lock:
			close(fd);
		}

		errno = 0;
	}

	closedir(dirp);

	if (0 != errno) {
		error("error while scanning poll directory - %m");
	}

	*pinfos = infos;

	return cnt;
}
