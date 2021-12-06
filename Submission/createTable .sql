CREATE TABLE User(
	UserID			VARCHAR(20) 	NOT NULL,
    Password		VARCHAR(20)		NOT NULL,
    Name			VARCHAR(20) 	NOT NULL,
    PRIMARY KEY (UserID));

CREATE TABLE Book(
	BookID			VARCHAR(10)		NOT NULL,
    Title			VARCHAR(150)	NOT NULL,
	PublicationYear	YEAR,
    Author			VARCHAR(500),
    Category		VARCHAR(500)	NOT NULL,
    PRIMARY KEY (BookID));

CREATE TABLE Fine(
    UserID			VARCHAR(20)		NOT NULL,
    FineDateTime	DATETIME		NOT NULL,
    FineAmount		SMALLINT		NOT NULL,
    PRIMARY KEY (UserID, FineDateTime),
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON UPDATE CASCADE);

CREATE TABLE Payment(
	PaymentID		VARCHAR(10)		NOT NULL,
    UserID			VARCHAR(20)		NOT NULL,
    PaymentDateTime	DATETIME 		DEFAULT NULL,
    PaymentAmount	SMALLINT		DEFAULT NULL,
    FineDateTime	DATETIME,
    FineUserID		VARCHAR(20),
    PRIMARY KEY (PaymentID),
    FOREIGN KEY (UserID) REFERENCES User(UserID) on UPDATE CASCADE,
    FOREIGN KEY (FineUserID, FineDateTime) REFERENCES Fine(UserID, FineDateTime) ON DELETE SET NULL);

CREATE TABLE LoanStatus(
	BookID		VARCHAR(10)		NOT NULL,
    UserID	    VARCHAR(20)     NOT NULL,
    ExpectedDueDate	DATETIME		NOT NULL,
    ExtensionStatus BOOLEAN		NOT NULL,
    PRIMARY KEY (BookID, UserID));

CREATE TABLE ReserveStatus(
	BookID		VARCHAR(10)		NOT NULL,
    UserID	    VARCHAR(20)     NOT NULL,
    ReserveDate	DATETIME		NOT NULL,
    PRIMARY KEY (BookID, UserID));
    
    
    
    
    


    
    
    
    
    
    