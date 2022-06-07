/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 */

#include <signal.h>
#include <stdlib.h>

#include "core/io.h"
#include "core/rest.h"
#include "utils/buf.h"
#include "utils/json.h"

#define ENGINE_CNT 3

static bool ping_engine(usize ID)
{
	char cmd[60];
	bool status;
	int err;

	snprintf(cmd, sizeof(cmd), "ping -c 1 -W 1 bixi-engine-%zu 2>&1 > /dev/null", ID);

	err    = system(cmd);
	status = false;

	if (err < 0) {
		warning("failed to ping engine %zu", ID);
	} else if (0 == err){
		status = true;
	}

	return status;
}

static enum http_status get(const char *user, const struct json *req, struct json **pres)
{
	(void)user;
	(void)req;

	enum http_status code;

	struct json *res;

	res = json_array();

	code = HTTP_OK;

	/*
	 * Fix bug where system(3) is waiting for its child, but ignoring
	 * SIGCHLD in main server loop prevent that!  This should probably be
	 * move into core/main.c
	 */
	signal(SIGCHLD, SIG_DFL);

	for (usize i=0; i<ENGINE_CNT; ++i) {

		bool status;

		status = ping_engine(i+1);

		if (!status) {
			code = HTTP_INTERNAL_SERVER_ERROR;
		}

		json_array_push(res, json_boolean(status));
	}

	*pres = res;

	return code;
}

REST_MAKE_URI = {
	.route	 = "/status",
	.get	 = &get,
};
