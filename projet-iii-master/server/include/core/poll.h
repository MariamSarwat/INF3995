#ifndef CORE_POLL_H
#define CORE_POLL_H

struct json;

extern int poll_put(const struct json *info);
extern long int poll_get(struct json **infos);

#endif
