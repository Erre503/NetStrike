IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Plugin' AND type = 'U')
BEGIN
    CREATE TABLE Plugin (
        idAtt int NOT NULL PRIMARY KEY,
        name varchar(50) NOT NULL,
        params varchar(200),
        description varchar(300)
    );
END;


IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'AttLog' AND type = 'U')
BEGIN
    CREATE TABLE AttLog (
        idLog int NOT NULL PRIMARY KEY,
        dateLog datetime NOT NULL,
        result varchar(300) NOT NULL,
        success bit NOT NULL, -- Use 'bit' for boolean values
        pluginUsed int NOT NULL,
        FOREIGN KEY (pluginUsed) REFERENCES Plugin(idAtt)
    );
END;