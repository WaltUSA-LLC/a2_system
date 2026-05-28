CREATE TABLE Operator (
    ID INT PRIMARY KEY,
    FirstName NVARCHAR(100) NOT NULL,
	LastName NVARCHAR(100),
);

CREATE TABLE ShiftOperator (
    ShiftStartTime DATETIME2 NOT NULL,
    OperatorID INT NOT NULL,
	RoleName NVARCHAR(100) NOT NULL,

    PRIMARY KEY (ShiftStartTime, OperatorID),
    FOREIGN KEY (OperatorID) REFERENCES Operator(ID)
);

--Operator
--9000 CHN
INSERT INTO Operator (ID, FirstName, LastName)
VALUES (0144, 'Franklin', 'Tucker');

INSERT INTO Operator (ID, FirstName, LastName)
VALUES (1055, 'Kandel', 'Mueller');

INSERT INTO Operator (ID, FirstName, LastName)
VALUES (1060, 'Jamie', NULL);

INSERT INTO Operator (ID, FirstName, LastName)
VALUES (9001, 'Lisa', 'Wan');

INSERT INTO Operator (ID, FirstName, LastName)
VALUES (9002, 'Sunny', 'Yuan');

INSERT INTO Operator (ID, FirstName, LastName)
VALUES (0184, 'Marlon', 'Hernandez');

INSERT INTO Operator (ID, FirstName, LastName)
VALUES (9003, 'Tim', 'Cao');

INSERT INTO Operator (ID, FirstName, LastName)
VALUES (9004, 'Qian', 'Liu');

INSERT INTO Operator (ID, FirstName, LastName)
VALUES (1008, 'Olga', 'Guitierrez');

INSERT INTO Operator (ID, FirstName, LastName)
VALUES (0202, 'Veronica', 'Casas');

INSERT INTO Operator (ID, FirstName, LastName)
VALUES (1067, 'Juanito', null);

INSERT INTO Operator (ID, FirstName, LastName)
VALUES (1063, 'Ismael', null);

INSERT INTO Operator (ID, FirstName, LastName)
VALUES (1061, 'Jearnny', 'Yan');

INSERT INTO Operator (ID, FirstName, LastName)
VALUES (1069, 'Shannon', null);

INSERT INTO Operator (ID, FirstName, LastName)
VALUES (1062, 'Danny', 'Franco');

INSERT INTO Operator (ID, FirstName, LastName)
VALUES (1071, 'Deliang', 'Han');