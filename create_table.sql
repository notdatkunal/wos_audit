use csilms
go

setuser 'dbo'
go

create table WOSMaster (
    WOSSerial            int           not null,
    CustomerCode         char(4)        not null,
    WOSType              char(3)        not null,
    InitiatedBy          char(8)        not null,
    DateTimeInitiated    datetime       not null,
    ConcurredBy          char(8)            null,
    DateTimeConcurred    datetime           null,
    WONumber             char(50)           null,
    WOIDate              datetime           null,
    ApprovedBy           char(8)            null,
    DateTimeApproved     datetime           null,
    SanctionNo           char(50)           null,
    SanctionDate         datetime           null,
    ClosedBy             char(8)            null,
    DateTimeClosed       datetime           null,
    Remarks              varchar(255)       null
)
lock allpages
on 'default'
go

alter table WOSMaster partition 1
go

setuser
go



use csilms
go

setuser 'dbo'
go

create table WOSLine (
    WOSSerial           int           not null,
    WOSLineSerial       int           not null,
    ItemCode            char(32)      not null,
    ItemDesc            char(60)      not null,
    ItemDeno            char(3)       not null,
    SOS                 char(3)       not null,
    AuthorisedQty       real          not null,
    ReceivedQty         real              null,
    BalanceQty          real              null,
    ReviewedQty         real              null,
    VettedQty           real              null,
    RecommendedQty      real              null,
    DateFromWhichHeld   datetime          null,
    AuthorityRef        varchar(255)  not null,
    AuthorityDate       datetime      not null,
    Justification       varchar(255)  not null,
    Price               money             null,
    TotalCost           money             null,
    Remarks             text              null,
    ClosedBy            char(8)           null,
    DateTimeClosed      datetime          null,

    constraint Chk_Price
        check (Price >= 0),

    constraint Chk_TotalCost
        check (TotalCost >= 0)
)
lock allpages
on 'default'
go

alter table WOSLine partition 2
go


CREATE TABLE CodeTable (
    ColumnName   CHAR(30)      NOT NULL,
    CodeValue    CHAR(10)      NOT NULL,
    Description  CHAR(30)      NULL
)
LOCK ALLPAGES
ON 'default';


CREATE TABLE Correspondence (
    LineNo                 INT            NOT NULL,
    TableName              CHAR(30)       NOT NULL,
    PrimaryKeyValue        VARCHAR(120)   NOT NULL,
    RoleName               CHAR(15)       NOT NULL,
    CorrespondenceBy       CHAR(8)        NOT NULL,
    CorrespondenceToRole   CHAR(15)       NOT NULL,
    DateTimeCorrespondence SMALLDATETIME  NOT NULL,
    CorrespondenceType     CHAR(5)        NOT NULL,
    StationCode            CHAR(1)        NOT NULL,
    Remarks                VARCHAR(255)   NULL,
    DocumentType           CHAR(30)       NULL,
    Document               IMAGE          NULL,
    CorrespondenceChoice   CHAR(1)        NULL
)
LOCK ALLPAGES
ON 'default';


CREATE TABLE UserRole (
    LoginId           CHAR(8)        NOT NULL,
    RoleName          CHAR(15)       NOT NULL,
    DateTimeActivated SMALLDATETIME  NOT NULL,
    DateTimeClosed    SMALLDATETIME  NULL,
    StationCode       CHAR(1)        NOT NULL,

    CONSTRAINT chk_UserRol_Stn_cd
    CHECK (StationCode IN ('K','U','B','V','D','P','A','G'))
)
LOCK ALLPAGES
ON 'default';


CREATE TABLE Users (
    LoginId        CHAR(8)        NOT NULL,
    Id             CHAR(8)        NOT NULL,
    Name           CHAR(30)       NOT NULL,
    Rank           CHAR(10)       NOT NULL,
    Department     CHAR(8)        NOT NULL,
    DateTimeJoined SMALLDATETIME  NOT NULL,
    DateTimeLeft   SMALLDATETIME  NULL,
    StationCode    CHAR(1)        NOT NULL,

    CONSTRAINT chk_Users_Stn_cd
    CHECK (StationCode IN ('K','U','B','V','D','P','A','G')),

    CONSTRAINT Users_LoginId
    CHECK (LoginId LIKE '[a-zA-Z]%')
)
LOCK ALLPAGES
ON 'default';
