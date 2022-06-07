/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 */

#include "core/io.h"
#include "core/poll.h"
#include "core/rest.h"
#include "utils/json.h"

static enum http_status get(const char *user, const struct json *req, struct json **res)
{
	(void)user;
	(void)req;

	struct json *infos;
	long int cnt;

	cnt = poll_get(&infos);

	switch (cnt) {
	case -1:
		return HTTP_BAD_REQUEST;
	case -2:
		return HTTP_INTERNAL_SERVER_ERROR;
	case 0:
		break;
	default:
		*res = infos;
	}

	return HTTP_OK;
}

static enum http_status put(const char *user, const struct json *req, struct json **res)
{
	(void)user;
	(void)res;

	enum http_status status;

	status = HTTP_BAD_REQUEST;

	if (!req) {
		goto bad_req;
	}

	switch (poll_put(req)) {
	case 0:
		status = HTTP_OK;
		break;
	case -2:
		status = HTTP_INTERNAL_SERVER_ERROR;
		break;
	}

bad_req:
	return status;
}

REST_MAKE_URI = {
	.route	 = "/sondage",
	.put	 = &put,
	.get     = &get,
	.options = REST_AUTH_GET
};
