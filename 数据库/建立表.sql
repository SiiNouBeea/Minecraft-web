-- 创建数据库
--CREATE DATABASE User_All
--GO

-- 使用User_All数据库
USE User_All;
GO


-- 创建序列-user
CREATE SEQUENCE User_Seq
    START WITH 10001
    INCREMENT BY 1;
GO



-- 创建用户基本信息表 (Users)
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

-- 创建用户权限表 (UserRoles)
CREATE TABLE UserRoles (
    RoleID INT PRIMARY KEY IDENTITY(1,1),
    RoleName NVARCHAR(50) NOT NULL
);
GO

-- 创建用户角色关联表 (UserRoles_Con)
CREATE TABLE UserRoles_Con (
    UserID INT,
    RoleID INT,
    PRIMARY KEY (UserID, RoleID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (RoleID) REFERENCES UserRoles(RoleID)
);
GO

-- 创建用户登录记录表 (UserLoginRecords)
CREATE TABLE UserLoginRecords (
    RecordID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT,
    LoginTime DATETIME DEFAULT GETDATE(),
    IPAddress NVARCHAR(15),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);
GO

--增加一列IP属地
ALTER TABLE UserLoginRecords
ADD Address NVARCHAR(15);

-- 创建用户个人资料表 (UserProfiles)
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

-- 为Users表添加Coins列
ALTER TABLE Users
ADD Coins INT DEFAULT 10;
GO

-- 为Users表添加Stars列
ALTER TABLE Users
ADD Stars INT DEFAULT 3;
GO

/*用户基本信息表 (Users)

UserID: INT类型，从10001开始自动递增，用户唯一标识符。
Username: NVARCHAR(50)类型，非空，用户名。
Password: NVARCHAR(128)类型，非空，加密后的用户密码。
Nickname: NVARCHAR(50)类型，非空，用户昵称。
Email: NVARCHAR(100)类型，用户电子邮件地址。
Phone: NVARCHAR(20)类型，用户电话号码。
CreatedAt: DATETIME类型，默认为当前时间，账户创建时间。
UpdatedAt: DATETIME类型，默认为当前时间，账户最后更新时间。
Coins: INT类型，默认为10，存储用户的硬币（虚拟货币）。
Stars: INT类型，默认为3，存储用户的星星（虚拟货币）。


用户权限表 (UserRoles)

RoleID: INT类型，自动递增，角色唯一标识符。
RoleName: NVARCHAR(50)类型，非空，角色名称。


用户角色关联表 (UserRoles_Con)

UserID: INT类型，用户ID。
RoleID: INT类型，角色ID。
复合主键由UserID和RoleID组成。
外键UserID引用Users表的UserID。
外键RoleID引用UserRoles表的RoleID。


用户登录记录表 (UserLoginRecords)

RecordID: INT类型，自动递增，登录记录唯一标识符。
UserID: INT类型，用户ID。
LoginTime: DATETIME类型，默认为当前时间，登录时间。
IPAddress: NVARCHAR(15)类型，登录IP地址。
外键UserID引用Users表的UserID。


用户个人资料表 (UserProfiles)

UserID: INT类型，用户ID。
FirstName: NVARCHAR(50)类型，用户名（名）。
LastName: NVARCHAR(50)类型，用户姓（姓）。
Birthday: DATE类型，出生日期。
Gender: NVARCHAR(10)类型，性别。
Bio: NVARCHAR(255)类型，个人简介。
外键UserID引用Users表的UserID，并且作为主键。
*/

-- 启用IDENTITY_INSERT
SET IDENTITY_INSERT UserRoles ON;
GO

-- 插入用户权限表数据
INSERT INTO UserRoles (RoleID, RoleName) VALUES
(1, 'Administrators'),
(2, 'Advanced_Users'),
(3, 'User'),
(4, 'Visitor'),
(5, 'Banned');
GO

-- 创建PlayerData表
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

--建立Genuine列
ALTER TABLE PlayerData
ADD Genuine BIT DEFAULT 0;
--建立PlayerDate
ALTER TABLE PlayerData
ADD PassDate DATE;


-- 禁用IDENTITY_INSERT
SET IDENTITY_INSERT UserRoles OFF;
GO


-- 创建一个新用户
CREATE LOGIN [czy] WITH PASSWORD = '1341';


-- 创建用户QQ关联表 (UserQQ_Con)
CREATE TABLE UserQQ_Con (
    UserID INT,
    QQID CHAR(16),
    PRIMARY KEY (UserID, QQID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
);
GO