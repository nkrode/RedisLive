CREATE TABLE info(datetime text,info text, server text);

CREATE TABLE keys(datetime text, expire number, persist number, server text);

CREATE TABLE memory(datetime text,current real,max real, server text);

CREATE TABLE "monitor" ("datetime" datetime,"command" text,"arguments" text,"server" text, keyname text);

CREATE INDEX "monitor_dateTime_Index" ON "monitor" ("datetime" DESC);

CREATE INDEX serverIndex on monitor(server);