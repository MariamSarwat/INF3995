/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 */


#include <stdlib.h>
#include <string.h>

#include "core/auth.h"
#include "core/io.h"
#include "utils/base64.h"
#include "utils/buf.h"
#include "utils/http.h"
#include "utils/json.h"

const char *http_method_names[] = {
	[HTTP_GET]    = "GET",
	[HTTP_PUT]    = "PUT",
	[HTTP_POST]   = "POST",
	[HTTP_PATCH]  = "PATCH",
	[HTTP_DELETE] = "DELETE"
};

int http_get_method(const char *method_name)
{
	int ret = -1;
	for (usize i=0; i<array_size(http_method_names); ++i) {
		if (streq(method_name, http_method_names[i])) {
			ret = i;
			break;
		}
	}
	return ret;
}

void http_clean(struct http_request *req)
{
	http_del_fields(req);

	if (req->URI) {
		free(req->URI);
	}

	if (req->authorization) {
		free(req->authorization);
	}
}

void http_add_field(struct http_request *request, const char *field)
{
	char *cpy;

	if (unlikely(NULL == index(field, ':'))) {
		return;
	}

	if (unlikely(!request->fields)) {
		buf_new(request->fields);
	}

	cpy = strdup(field);

	buf_push(request->fields, &cpy);
}

void http_del_fields(struct http_request *request)
{
	char **it;

	if (!request->fields) {
		return;
	}

	buf_for_each(it, request->fields) {
		free(*it);
	}
	buf_del(request->fields);
	request->fields = NULL;
}

const char *http_field_value(const struct http_request *request, const char *field_name)
{
	char **it;

	if (!request->fields) {
		goto no_field;
	}

	buf_for_each(it, request->fields) {

		const char *name;
		usize len;

		name = *it;
		len  = index(name, ':') - name;

		if (0 == strncasecmp(field_name, name, len)) {
			return name + len + 1;
		}
	}
no_field:
	return NULL;
}

void http_set_URI(struct http_request *request, const char *URI)
{
	if (request->URI) {
		free(request->URI);
	}

	request->URI = strdup(URI);
}


void http_del_URI(struct http_request *request)
{
	if (request->URI) {
		free(request->URI);
		request->URI = NULL;
	}
}

const char *http_status_string(enum http_status status)
{
	switch (status) {
#define X(NAME, STATUS) case CAT(HTTP_, NAME): return STR(NAME);
#include "utils/http.xlist"
#undef X
	}

	__builtin_unreachable();
}

enum http_status http_auth(const struct http_request *req, char **puser)
{
	static const char auth_method[] = "Basic ";

	enum http_status granted;
	char *user, *passwd;
	char *authorization;
	char *saveptr;
	char *saved_user;

	/* Search for - Authorization: */
	authorization = req->authorization;
	granted	      = HTTP_UNAUTHORIZED;
	saved_user    = NULL;

	if (!authorization) {
		warning("missing authorization field");
		goto no_auth;
	}

	/* Search for - Authorization: Base  */
	authorization = strstr(authorization, auth_method);

	if (!authorization) {
		goto bad_auth_method;
	}

	/* Now we're at the begining of the base64 credentials */
	authorization += sizeof(auth_method) - 1;

	/* Decoded bas64 */
	authorization = base64_decode(authorization);

	saveptr = NULL;
	user	= strtok_r(authorization, ":", &saveptr);

	info("authenticating user '%s'", user);

	if (!user) {
		goto bad_user;
	}

	saved_user = strdup(user);

	passwd = strtok_r(NULL, ":", &saveptr);

	if (!passwd) {
		goto bad_passwd;
	}

	if (auth_authenticate(user, passwd)) {
		granted = HTTP_OK;
	}

bad_passwd:
bad_user:
	buf_del(authorization);

bad_auth_method:
no_auth:
	*puser = saved_user;

	return granted;
}

bool http_auth_set(const char *user, const char *passwd)
{
	return auth_change(user, passwd) == 0;
}
