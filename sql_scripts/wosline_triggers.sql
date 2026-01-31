-- SQL Script to create INSERT and UPDATE triggers on WOSLine table
-- These triggers validate that VettedQty should not be greater than AuthorisedQty

USE auditdb
GO

-- Drop existing triggers if they exist
IF EXISTS (SELECT 1 FROM sysobjects WHERE name = 'trg_WOSLine_Insert_VettedQty' AND type = 'TR')
    DROP TRIGGER trg_WOSLine_Insert_VettedQty
GO

IF EXISTS (SELECT 1 FROM sysobjects WHERE name = 'trg_WOSLine_Update_VettedQty' AND type = 'TR')
    DROP TRIGGER trg_WOSLine_Update_VettedQty
GO

-- INSERT Trigger: Prevent insert if VettedQty > AuthorisedQty
CREATE TRIGGER trg_WOSLine_Insert_VettedQty
ON WOSLine
FOR INSERT
AS
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM inserted 
        WHERE VettedQty IS NOT NULL 
          AND VettedQty > AuthorisedQty
    )
    BEGIN
        RAISERROR 50001 'VettedQty cannot be greater than AuthorisedQty'
        ROLLBACK TRANSACTION
        RETURN
    END
END
GO

-- UPDATE Trigger: Prevent update if VettedQty > AuthorisedQty
CREATE TRIGGER trg_WOSLine_Update_VettedQty
ON WOSLine
FOR UPDATE
AS
BEGIN
    -- Only check if VettedQty or AuthorisedQty was updated
    IF UPDATE(VettedQty) OR UPDATE(AuthorisedQty)
    BEGIN
        IF EXISTS (
            SELECT 1 
            FROM inserted 
            WHERE VettedQty IS NOT NULL 
              AND VettedQty > AuthorisedQty
        )
        BEGIN
            RAISERROR 50001 'VettedQty cannot be greater than AuthorisedQty'
            ROLLBACK TRANSACTION
            RETURN
        END
    END
END
GO

PRINT 'WOSLine triggers created successfully'
GO
