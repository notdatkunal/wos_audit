-- do not use this script
disk init
name = "userdev1",
physname = "C:\SAP\data\userdev1.dat",
size = "500M"
go

create database test
on userdev1 = '300M'
log on userdev1 = '100M'
with override
go



select * from Users


UPDATE dbo.Users SET StationCode='B' 
