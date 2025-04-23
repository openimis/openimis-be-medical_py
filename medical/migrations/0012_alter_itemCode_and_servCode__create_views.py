from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('medical', '0011_rename_servicelinkeditem_serviceitem_parent_and_more'),
    ]
    operations = [
         migrations.AlterField(
            model_name='item',
            name='code',
            field=models.CharField(db_column='ItemCode', max_length=50),
        ),
        migrations.AlterField(
            model_name='service',
            name='code',
            field=models.CharField(db_column='ServCode', max_length=50),
        ),
         migrations.RunSQL(

            """
            CREATE OR REPLACE VIEW "public"."uvwItemExpenditures" AS
            SELECT 
                SUM("CI"."RemuneratedAmount") AS "ItemExpenditure",
                MONTH(coalesce("C"."DateTo", "C"."DateFrom")) AS "MonthTime",
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) AS "QuarterTime",
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")) AS "YearTime",
                "R"."RegionName" AS "Region",
                "HFD"."DistrictName",
                "PR"."ProductCode",
                "PR"."ProductName",
                DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")) AS "Age",
                "I"."Gender",
                "Itm"."ItemType",
                "Itm"."ItemCode",
                "Itm"."ItemName",
                CASE
                    WHEN DATEDIFF_DAY("C"."DateFrom", "C"."DateTo") > 0 THEN 'I'
                    ELSE 'O'
                END AS "ItemCareType",
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "C"."VisitType",
                "ICD"."ICDCode",
                "ICD"."ICDName",
                "DIns"."DistrictName" AS "IDistrictName",
                "W"."WardName",
                "V"."VillageName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion",
                "HFR"."RegionName" AS "ProdRegion"
            FROM "tblClaimItems" "CI"
            INNER JOIN "tblClaim" "C" ON "CI"."ClaimID" = "C"."ClaimID"
            INNER JOIN "tblProduct" "PR" ON "CI"."ProdID" = "PR"."ProdID"
            INNER JOIN "tblInsuree" "I" ON "C"."InsureeID" = "I"."InsureeID"
            INNER JOIN "tblFamilies" "F" ON "I"."FamilyID" = "F"."FamilyID"
            INNER JOIN "tblVillages" "V" ON "V"."VillageId" = "F"."LocationId"
            INNER JOIN "tblWards" "W" ON "W"."WardId" = "V"."WardId"
            INNER JOIN "tblDistricts" "DIns" ON "DIns"."DistrictId" = "W"."DistrictId"
            INNER JOIN "tblItems" "Itm" ON "CI"."ItemID" = "Itm"."ItemID"
            INNER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
            INNER JOIN "tblICDCodes" "ICD" ON "C"."ICDID" = "ICD"."ICDID"
            INNER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
            INNER JOIN "tblRegions" "R" ON "DIns"."Region" = "R"."RegionId"
            INNER JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "CI"."ValidityTo" IS NULL
              AND "C"."ValidityTo" IS NULL
              AND "PR"."ValidityTo" IS NULL
              AND "I"."ValidityTo" IS NULL
              AND "HF"."ValidityTo" IS NULL
              AND "HFD"."ValidityTo" IS NULL
              AND "C"."ClaimStatus" >= 8
            GROUP BY 
                MONTH(coalesce("C"."DateTo", "C"."DateFrom")),
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")),
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")),
                "R"."RegionName",
                "PR"."ProductCode",
                "PR"."ProductName",
                DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")),
                "I"."Gender",
                "Itm"."ItemType",
                "Itm"."ItemCode",
                "Itm"."ItemName",
                DATEDIFF_DAY("C"."DateFrom", "C"."DateTo"),
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "C"."VisitType",
                "ICD"."ICDCode",
                "ICD"."ICDName",
                "DIns"."DistrictName",
                "W"."WardName",
                "V"."VillageName",
                "HFD"."DistrictName",
                "HFR"."RegionName";
            """,
        ),

        migrations.RunSQL(
            
            """
            CREATE OR REPLACE VIEW "public"."uvwItemUtilization" AS
            SELECT 
                SUM("CI"."QtyProvided") AS "ItemUtilized", 
                MONTH(coalesce("C"."DateTo", "C"."DateFrom")) AS "MonthTime", 
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) AS "QuarterTime", 
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")) AS "YearTime", 
                "R"."RegionName" AS "Region", 
                "DIns"."DistrictName", 
                "Prod"."ProductCode", 
                "Prod"."ProductName", 
                DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")) AS "Age", 
                "I"."Gender", 
                "Itm"."ItemType", 
                "Itm"."ItemCode", 
                "Itm"."ItemName", 
                CASE 
                    WHEN DATEDIFF_DAY("C"."DateFrom", "C"."DateTo") > 0 THEN 'I' 
                    ELSE 'O' 
                END AS "ItemCareType", 
                "HF"."HFLevel", 
                "HF"."HFCode", 
                "HF"."HFName", 
                "ICD"."ICDCode", 
                "ICD"."ICDName", 
                "DIns"."DistrictName" AS "IDistrictName", 
                "W"."WardName", 
                "V"."VillageName", 
                "HFD"."DistrictName" AS "HFDistrict", 
                "C"."VisitType", 
                "HFR"."RegionName" AS "HFRegion", 
                "R"."RegionName" AS "ProdRegion"
            FROM public."tblClaimItems" AS "CI"
            INNER JOIN public."tblClaim" AS "C" ON "C"."ClaimID" = "CI"."ClaimID" 
            LEFT OUTER JOIN public."tblProduct" AS "Prod" ON "CI"."ProdID" = "Prod"."ProdID" 
            INNER JOIN public."tblInsuree" AS "I" ON "C"."InsureeID" = "I"."InsureeID" 
            INNER JOIN public."tblFamilies" AS "F" ON "I"."FamilyID" = "F"."FamilyID" 
            INNER JOIN public."tblVillages" AS "V" ON "V"."VillageId" = "F"."LocationId" 
            INNER JOIN public."tblWards" AS "W" ON "W"."WardId" = "V"."WardId" 
            INNER JOIN public."tblDistricts" AS "DIns" ON "DIns"."DistrictId" = "W"."DistrictId" 
            INNER JOIN public."tblItems" AS "Itm" ON "CI"."ItemID" = "Itm"."ItemID" 
            INNER JOIN public."tblHF" AS "HF" ON "C"."HFID" = "HF"."HfID" 
            INNER JOIN public."tblICDCodes" AS "ICD" ON "C"."ICDID" = "ICD"."ICDID" 
            INNER JOIN public."tblDistricts" AS "HFD" ON "HF"."LocationId" = "HFD"."DistrictId" 
            INNER JOIN public."tblRegions" AS "R" ON "R"."RegionId" = "DIns"."Region" 
            INNER JOIN public."tblRegions" AS "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE ("CI"."ValidityTo" IS NULL) 
              AND ("C"."ValidityTo" IS NULL) 
              AND ("Prod"."ValidityTo" IS NULL) 
              AND ("Itm"."ValidityTo" IS NULL) 
              AND ("HF"."ValidityTo" IS NULL) 
              AND ("HFD"."ValidityTo" IS NULL) 
              AND ("C"."ClaimStatus" > 2)
              AND "CI"."RejectionReason" = 0
            GROUP BY 
                MONTH(coalesce("C"."DateTo", "C"."DateFrom")), 
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")), 
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")), 
                "R"."RegionName", 
                "Prod"."ProductCode", 
                "Prod"."ProductName", 
                DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")), 
                "I"."Gender", 
                "Itm"."ItemType", 
                "Itm"."ItemCode", 
                "Itm"."ItemName", 
                DATEDIFF_DAY("C"."DateFrom", "C"."DateTo"), 
                "HF"."HFLevel", 
                "HF"."HFCode", 
                "HF"."HFName", 
                "ICD"."ICDCode", 
                "ICD"."ICDName", 
                "DIns"."DistrictName", 
                "W"."WardName", 
                "V"."VillageName",  
                "C"."VisitType", 
                "HFD"."DistrictName", 
                "HFR"."RegionName";
            """,
        ),
        migrations.RunSQL(

            """
            CREATE OR REPLACE VIEW "public"."uvwServiceUtilization" AS
            SELECT  
                SUM("CS"."QtyProvided") AS ServiceUtilized, 
                MONTH(coalesce("C"."DateTo", "C"."DateFrom")) AS MonthTime, 
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) AS QuarterTime, 
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")) AS YearTime, 
                "R"."RegionName" AS "Region", 
                "DIns"."DistrictName",  
                "Prod"."ProductCode", 
                "Prod"."ProductName", 
                DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")) AS "Age", 
                "I"."Gender", 
                "S"."ServType", 
                "S"."ServCode", 
                "S"."ServName", 
                CASE 
                    WHEN DATEDIFF_DAY("C"."DateFrom", "C"."DateTo") > 0 THEN N'I' 
                    ELSE N'O' 
                END AS "ServCareType", 
                "HF"."HFLevel", 
                "HF"."HFCode", 
                "HF"."HFName", 
                "C"."VisitType", 
                "ICD"."ICDCode", 
                "ICD"."ICDName", 
                "DIns"."DistrictName" AS "IDistrictName", 
                "W"."WardName", 
                "V"."VillageName", 
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion", 
                "R"."RegionName" AS "ProdRegion"
            FROM public."tblClaimServices" AS "CS" 
            INNER JOIN public."tblClaim" AS "C" ON "CS"."ClaimID" = "C"."ClaimID" 
            LEFT OUTER JOIN public."tblProduct" AS "Prod" ON "CS"."ProdID" = "Prod"."ProdID" 
            INNER JOIN public."tblInsuree" AS "I" ON "C"."InsureeID" = "I"."InsureeID" 
            INNER JOIN public."tblFamilies" AS "F" ON "I"."FamilyID" = "F"."FamilyID" 
            INNER JOIN public."tblVillages" AS "V" ON "V"."VillageId" = "F"."LocationId" 
            INNER JOIN public."tblWards" AS "W" ON "W"."WardId" = "V"."WardId"
            INNER JOIN public."tblDistricts" AS "DIns" ON "DIns"."DistrictId" = "W"."DistrictId" 
            INNER JOIN public."tblServices" AS "S" ON "CS"."ServiceID" = "S"."ServiceID" 
            INNER JOIN public."tblHF" AS "HF" ON "C"."HFID" = "HF"."HfID" 
            INNER JOIN public."tblICDCodes" AS "ICD" ON "C"."ICDID" = "ICD"."ICDID" 
            INNER JOIN public."tblDistricts" AS "HFD" ON "HF"."LocationId" = "HFD"."DistrictId" 
            INNER JOIN public."tblRegions" AS "R" ON "R"."RegionId" = "DIns"."Region" 
            INNER JOIN public."tblRegions" AS "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE ("CS"."ValidityTo" IS NULL) 
              AND ("C"."ValidityTo" IS NULL) 
              AND ("Prod"."ValidityTo" IS NULL) 
              AND ("I"."ValidityTo" IS NULL) 
              AND ("DIns"."ValidityTo" IS NULL) 
              AND ("HF"."ValidityTo" IS NULL) 
              AND ("HFD"."ValidityTo" IS NULL) 
              AND ("F"."ValidityTo" IS NULL) 
              AND ("S"."ValidityTo" IS NULL) 
              AND ("C"."ClaimStatus" > 2)
              AND "CS"."RejectionReason" = 0
            GROUP BY 
                MONTH(coalesce("C"."DateTo", "C"."DateFrom")), 
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")), 
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")), 
                "R"."RegionName", 
                "Prod"."ProductCode", 
                "Prod"."ProductName", 
                DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")), 
                "I"."Gender", 
                "S"."ServType", 
                "S"."ServCode", 
                "S"."ServName", 
                DATEDIFF_DAY("C"."DateFrom", "C"."DateTo"), 
                "HF"."HFLevel", 
                "HF"."HFCode", 
                "HF"."HFName", 
                "C"."VisitType", 
                "ICD"."ICDCode", 
                "ICD"."ICDName", 
                "DIns"."DistrictName", 
                "W"."WardName", 
                "V"."VillageName", 
                "HFD"."DistrictName",  
                "HFR"."RegionName";
            """,
        ),
        migrations.RunSQL(

            """
            CREATE OR REPLACE VIEW "public"."uvwItemExpenditures" AS
            SELECT 
                SUM("CI"."RemuneratedAmount") AS "ItemExpenditure",
                MONTH(coalesce("C"."DateTo", "C"."DateFrom")) AS "MonthTime",
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) AS "QuarterTime",
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")) AS "YearTime",
                "R"."RegionName" AS "Region",
                "HFD"."DistrictName",
                "PR"."ProductCode",
                "PR"."ProductName",
                DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")) AS "Age",
                "I"."Gender",
                "Itm"."ItemType",
                "Itm"."ItemCode",
                "Itm"."ItemName",
                CASE
                    WHEN DATEDIFF_DAY("C"."DateFrom", "C"."DateTo") > 0 THEN 'I'
                    ELSE 'O'
                END AS "ItemCareType",
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "C"."VisitType",
                "ICD"."ICDCode",
                "ICD"."ICDName",
                "DIns"."DistrictName" AS "IDistrictName",
                "W"."WardName",
                "V"."VillageName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion",
                "HFR"."RegionName" AS "ProdRegion"
            FROM "tblClaimItems" "CI"
            INNER JOIN "tblClaim" "C" ON "CI"."ClaimID" = "C"."ClaimID"
            INNER JOIN "tblProduct" "PR" ON "CI"."ProdID" = "PR"."ProdID"
            INNER JOIN "tblInsuree" "I" ON "C"."InsureeID" = "I"."InsureeID"
            INNER JOIN "tblFamilies" "F" ON "I"."FamilyID" = "F"."FamilyID"
            INNER JOIN "tblVillages" "V" ON "V"."VillageId" = "F"."LocationId"
            INNER JOIN "tblWards" "W" ON "W"."WardId" = "V"."WardId"
            INNER JOIN "tblDistricts" "DIns" ON "DIns"."DistrictId" = "W"."DistrictId"
            INNER JOIN "tblItems" "Itm" ON "CI"."ItemID" = "Itm"."ItemID"
            INNER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
            INNER JOIN "tblICDCodes" "ICD" ON "C"."ICDID" = "ICD"."ICDID"
            INNER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
            INNER JOIN "tblRegions" "R" ON "DIns"."Region" = "R"."RegionId"
            INNER JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "CI"."ValidityTo" IS NULL
              AND "C"."ValidityTo" IS NULL
              AND "PR"."ValidityTo" IS NULL
              AND "I"."ValidityTo" IS NULL
              AND "HF"."ValidityTo" IS NULL
              AND "HFD"."ValidityTo" IS NULL
              AND "C"."ClaimStatus" >= 8
            GROUP BY 
                MONTH(coalesce("C"."DateTo", "C"."DateFrom")),
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")),
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")),
                "R"."RegionName",
                "PR"."ProductCode",
                "PR"."ProductName",
                DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")),
                "I"."Gender",
                "Itm"."ItemType",
                "Itm"."ItemCode",
                "Itm"."ItemName",
                DATEDIFF_DAY("C"."DateFrom", "C"."DateTo"),
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "C"."VisitType",
                "ICD"."ICDCode",
                "ICD"."ICDName",
                "DIns"."DistrictName",
                "W"."WardName",
                "V"."VillageName",
                "HFD"."DistrictName",
                "HFR"."RegionName";
            """
        ),
       
    ]
