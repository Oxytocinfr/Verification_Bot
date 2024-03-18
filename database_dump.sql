BEGIN TRANSACTION;
CREATE TABLE email (
                      id INTEGER PRIMARY KEY,
                      user_id TEXT NOT NULL,
                      email TEXT NOT NULL);
INSERT INTO "email" VALUES(1,'1014874125271044146','test@gmail.com');
COMMIT;
