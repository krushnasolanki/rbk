--# SET TERMINATOR @
-- UPDATE PARENT_OPPORTUNITIES TABLE WITH CSCORE, TOTAL TCV AMT AND TRANSLATED SALES STAGE CD
-- RETURNS UPDATED ROW COUNT -- SHOULD BE AT LEAST 1
CREATE PROCEDURE q2chub.sp_update_parent_opportunity(IN in_root_oppty_num VARCHAR(20),
                                                     IN in_cscore_num DECIMAL(17, 2),
                                                     IN in_tcv_amount DECIMAL(17, 2),
                                                     IN in_salesstage_cd CHAR(2),
                                                     OUT out_rowupdate_count SMALLINT)
    LANGUAGE SQL
BEGIN
    UPDATE q2chub.parent_opportunities
    SET be_cscore_num    = in_cscore_num,
        beusd_tcv_amt    = in_tcv_amount,
        be_salesstage_cd = in_salesstage_cd
    WHERE parent_oppty_num = in_root_oppty_num;
    GET DIAGNOSTICS out_rowupdate_count = ROW_COUNT;
END;