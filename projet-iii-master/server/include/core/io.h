#ifndef IO_H
#define IO_H

#include <stdlib.h>
#include <syslog.h>

#define debug(FMT, ARGS...)    syslog(LOG_DEBUG, FMT, ##ARGS)
#define info(FMT, ARGS...)     syslog(LOG_INFO, FMT, ##ARGS)
#define warning(FMT, ARGS...)  syslog(LOG_WARNING, FMT, ##ARGS)
#define error(FMT, ARGS...)    syslog(LOG_ERR, FMT, ##ARGS)
#define critical(FMT, ARGS...) syslog(LOG_CRIT, FMT, ##ARGS)
#define panic(FMT, ARGS...)    syslog(LOG_ALERT, FMT, ##ARGS); exit(EXIT_FAILURE)

#endif
