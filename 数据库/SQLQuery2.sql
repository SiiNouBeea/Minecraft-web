use User_All

select * from Users
select * from PlayerData
select * from UserLoginRecords
select * from UserProfiles
select * from UserRoles
select * from UserRoles_Con
select * from UserQQ_Con


INSERT INTO Users (Username, Password, Nickname, Email, Phone) VALUES ('118452954', '12222', '1222', '1@2222222', '18968218863')

SELECT Username, Email, Phone FROM Users WHERE Username = '118452950' OR Email = '1@22' OR Phone = '1'

INSERT INTO UserLoginRecords (UserID, IPAddress, Address) VALUES (10015, '127.0.0.1', '本地或特殊保留地址--')

--查询表中所有列
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Users'

--更新用户权限
UPDATE UserRoles_Con
SET RoleID = 2
WHERE UserID = 10016;

--带格式查询
SELECT FORMAT(Birthday, 'yyyy-MM-dd') AS FormattedDate FROM UserProfiles WHERE UserID = 10015;

--补全数据
INSERT INTO UserProfiles (UserID, FirstName, Lastname, Birthday, Gender, Bio) VALUES (10018, '222', '2', '2011-1-01', '沃尔玛购物袋', '没有简介')
INSERT INTO PlayerData (uuid, PlayerName, WhiteState) VALUES ('650376b4-bb0c-4c29-a125-57ce17f00fc8', 'SiiNouBeea', 1)
--修改数据
UPDATE PlayerData
SET WhiteState = 0, PassDate = NULL
WHERE UserID = 10031;


ALTER TABLE UserQQ_Con ALTER COLUMN QQID char(16);

SELECT UserID FROM Users

SELECT CASE WHEN EXISTS (SELECT 1 FROM User_ALL.dbo.UserQQ_Con WHERE UserID = 10015) THEN (SELECT QQID FROM User_ALL.dbo.UserQQ_Con WHERE UserID = 10015) ELSE CAST(0 AS BIT) END AS QQID

SELECT CASE WHEN EXISTS (SELECT 1 FROM User_ALL.dbo.UserQQ_Con WHERE QQID = '2837803638') THEN (SELECT UserID FROM User_ALL.dbo.UserQQ_Con WHERE QQID = '2837803638' ) ELSE CAST(0 AS BIT) END AS UserID