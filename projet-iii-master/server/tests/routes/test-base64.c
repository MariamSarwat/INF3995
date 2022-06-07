/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 */

#include "core/io.h"
#include "core/rest.h"
#include "utils/base64.h"
#include "utils/buf.h"

#include "./test-base64-strings.h"

static enum http_status get(const char *user, const struct json *req, struct json **res)
{
	(void)user;
	(void)req;
	(void)res;

	enum http_status status;

	status = HTTP_OK;

	for (usize i=0; i<array_size(base64_test_vector); ++i) {
		const char *encoded, *decoded;

		encoded = base64_encode(base64_test_vector[i].raw);

		if (!streq(encoded, base64_test_vector[i].encoded)) {
			error("fail to encode base64 %zu. expected '%s', got '%s'",
			      i, base64_test_vector[i].encoded, encoded);
			status = HTTP_IM_A_TEAPOT;
			continue;
		}

		decoded = base64_decode(encoded);

		if (!streq(decoded, base64_test_vector[i].raw)) {
			error("fail to decode base64 %zu", i);
			status = HTTP_IM_A_TEAPOT;
		}

		buf_del(encoded);
		buf_del(decoded);
	}

	/* Check for bad padding */
	{
		const char *result;

		result = base64_decode("BAD-PADDING");
		if (result) {
			error("base64: BAD-PADDING - %s", result);
			buf_del(result);
			status = HTTP_IM_A_TEAPOT;

		}
	}

	return status;
}

REST_MAKE_URI = {
	.route = "/base64",
	.get   = get
};
