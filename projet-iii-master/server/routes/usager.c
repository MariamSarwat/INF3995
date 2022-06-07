/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 */

#include "core/io.h"
#include "core/rest.h"
#include "utils/json.h"

static enum http_status post(const char *user, const struct json *req, struct json **res)
{
	/* Empty method */
	(void)user;
	(void)req;
	(void)res;

	return HTTP_OK;
}

static enum http_status put(const char *user, const struct json *req, struct json **res)
{
	enum http_status status;
	const struct json *new_passwd;

	(void)res;

	status = HTTP_BAD_REQUEST;

	if (!req) {
		goto no_req_body;
	}

	new_passwd = json_dict_get(req, "nouveau");

	if (new_passwd) {
		if (json_is_string(new_passwd)) {

			if (http_auth_set(user, json_to_string(new_passwd))) {
				info("setting new passwd for user %s", user);
				status = HTTP_OK;
			}
		}
	}

no_req_body:
	return status;
}

REST_MAKE_URI = {
	.route	 = "/usager/login",
	.post	 = &post,
	.options = REST_AUTH_ALL,
};

REST_MAKE_URI = {
	.route	 = "/usager/motdepasse",
	.put	 = &put,
	.options = REST_AUTH_ALL,
};
