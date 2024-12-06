-- �������ݿ�
--CREATE DATABASE User_All
--GO

-- ʹ��User_All���ݿ�
USE User_All;
GO


-- ��������-user
CREATE SEQUENCE User_Seq
    START WITH 10001
    INCREMENT BY 1;
GO



-- �����û�������Ϣ�� (Users)
CREATE TABLE Users (
    UserID INT DEFAULT NEXT VALUE FOR User_Seq PRIMARY KEY,
    Username NVARCHAR(50) NOT NULL,
    Password NVARCHAR(128) NOT NULL,
    Nickname NVARCHAR(50) NOT NULL,
    Email NVARCHAR(100),
    Phone NVARCHAR(20),
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE()
);
GO

-- �����û�Ȩ�ޱ� (UserRoles)
CREATE TABLE UserRoles (
    RoleID INT PRIMARY KEY IDENTITY(1,1),
    RoleName NVARCHAR(50) NOT NULL
);
GO

-- �����û���ɫ������ (UserRoles_Con)
CREATE TABLE UserRoles_Con (
    UserID INT,
    RoleID INT,
    PRIMARY KEY (UserID, RoleID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (RoleID) REFERENCES UserRoles(RoleID)
);
GO

-- �����û���¼��¼�� (UserLoginRecords)
CREATE TABLE UserLoginRecords (
    RecordID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT,
    LoginTime DATETIME DEFAULT GETDATE(),
    IPAddress NVARCHAR(15),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);
GO

--����һ��IP����
ALTER TABLE UserLoginRecords
ADD Address NVARCHAR(15);

-- �����û��������ϱ� (UserProfiles)
CREATE TABLE UserProfiles (
    UserID INT,
    FirstName NVARCHAR(50),
    LastName NVARCHAR(50),
    Birthday DATE,
    Gender NVARCHAR(10),
    Bio NVARCHAR(255),
    PRIMARY KEY (UserID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);
GO

-- ΪUsers�����Coins��
ALTER TABLE Users
ADD Coins INT DEFAULT 10;
GO

-- ΪUsers�����Stars��
ALTER TABLE Users
ADD Stars INT DEFAULT 3;
GO

/*�û�������Ϣ�� (Users)

UserID: INT���ͣ���10001��ʼ�Զ��������û�Ψһ��ʶ����
Username: NVARCHAR(50)���ͣ��ǿգ��û�����
Password: NVARCHAR(128)���ͣ��ǿգ����ܺ���û����롣
Nickname: NVARCHAR(50)���ͣ��ǿգ��û��ǳơ�
Email: NVARCHAR(100)���ͣ��û������ʼ���ַ��
Phone: NVARCHAR(20)���ͣ��û��绰���롣
CreatedAt: DATETIME���ͣ�Ĭ��Ϊ��ǰʱ�䣬�˻�����ʱ�䡣
UpdatedAt: DATETIME���ͣ�Ĭ��Ϊ��ǰʱ�䣬�˻�������ʱ�䡣
Coins: INT���ͣ�Ĭ��Ϊ10���洢�û���Ӳ�ң�������ң���
Stars: INT���ͣ�Ĭ��Ϊ3���洢�û������ǣ�������ң���


�û�Ȩ�ޱ� (UserRoles)

RoleID: INT���ͣ��Զ���������ɫΨһ��ʶ����
RoleName: NVARCHAR(50)���ͣ��ǿգ���ɫ���ơ�


�û���ɫ������ (UserRoles_Con)

UserID: INT���ͣ��û�ID��
RoleID: INT���ͣ���ɫID��
����������UserID��RoleID��ɡ�
���UserID����Users���UserID��
���RoleID����UserRoles���RoleID��


�û���¼��¼�� (UserLoginRecords)

RecordID: INT���ͣ��Զ���������¼��¼Ψһ��ʶ����
UserID: INT���ͣ��û�ID��
LoginTime: DATETIME���ͣ�Ĭ��Ϊ��ǰʱ�䣬��¼ʱ�䡣
IPAddress: NVARCHAR(15)���ͣ���¼IP��ַ��
���UserID����Users���UserID��


�û��������ϱ� (UserProfiles)

UserID: INT���ͣ��û�ID��
FirstName: NVARCHAR(50)���ͣ��û�����������
LastName: NVARCHAR(50)���ͣ��û��գ��գ���
Birthday: DATE���ͣ��������ڡ�
Gender: NVARCHAR(10)���ͣ��Ա�
Bio: NVARCHAR(255)���ͣ����˼�顣
���UserID����Users���UserID��������Ϊ������
*/

-- ����IDENTITY_INSERT
SET IDENTITY_INSERT UserRoles ON;
GO

-- �����û�Ȩ�ޱ�����
INSERT INTO UserRoles (RoleID, RoleName) VALUES
(1, 'Administrators'),
(2, 'Advanced_Users'),
(3, 'User'),
(4, 'Visitor'),
(5, 'Banned');
GO

-- ����PlayerData��
CREATE TABLE PlayerData (
    PlayerID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT,
    RoleID INT,
    uuid CHAR(64) NOT NULL,
    PlayerName CHAR(32) NOT NULL,
    WhiteState BIT NOT NULL,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (RoleID) REFERENCES UserRoles(RoleID),
);
GO

--����Genuine��
ALTER TABLE PlayerData
ADD Genuine BIT DEFAULT 0;
--����PlayerDate
ALTER TABLE PlayerData
ADD PassDate DATE;


-- ����IDENTITY_INSERT
SET IDENTITY_INSERT UserRoles OFF;
GO


-- ����һ�����û�
CREATE LOGIN [czy] WITH PASSWORD = '1341';


-- �����û�QQ������ (UserQQ_Con)
CREATE TABLE UserQQ_Con (
    UserID INT,
    QQID CHAR(16),
    PRIMARY KEY (UserID, QQID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
);
GO