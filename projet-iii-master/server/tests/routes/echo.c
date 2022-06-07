/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 *
 * tests/routes/echo.c - Echo back request in JSON
 */

#include "core/io.h"
#include "core/rest.h"
#include "utils/json.h"

static const char URI[] = "/test/echo";

static enum http_status get(const char *user, const struct json *req, struct json **pres)
{
	(void)user;
	(void)req;

	struct json *res;

	res = json_dict();

	json_dict_set(res, "method", json_string("GET"));
	json_dict_set(res, "URI", json_string(URI));
	json_dict_set(res, "status", json_string("OK"));

	*pres = res;

	return HTTP_OK;
}

static enum http_status put(const char *user, const struct json *req, struct json **pres)
{
	(void)user;

	char *req_str;
	struct json *res;

	if (!req) {
		goto no_req;
	}

	req_str	 = json_stringify(req);
	res	 = json_dict();

	json_dict_set(res, "method", json_string("GET"));
	json_dict_set(res, "URI", json_string(URI));
	json_dict_set(res, "request-body", json_string(req_str));
	json_dict_set(res, "status", json_number(HTTP_ACCEPTED));

	*pres = res;

	free(req_str);
no_req:
	return HTTP_ACCEPTED;
}

REST_MAKE_URI = {
	.route = URI,
	.get   = &get,
	.put   = &put,
};
