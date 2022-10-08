CREATE OR REPLACE
PROCEDURE q2chub.sp_update_buying_event_bom(IN in_root_oppty_num VARCHAR(20),
                                            IN in_cscore_num DECIMAL(17,2),
                                            IN in_tcv_amount DECIMAL(17,2),
                                            IN in_salesstage_cd CHAR(2),
                                            OUT out_rowupdate_count SMALLINT)
LANGUAGE SQL
BEGIN
    UPDATE
    q2chub.buying_event_bom
SET
    be_cscore_num = in_cscore_num,
    beusd_tcv_amt = in_tcv_amount,
    be_sales_stage_cd = in_salesstage_cd,
    update_id = 'QUESTESA',
    update_ts = CURRENT TIMESTAMP
WHERE
    root_oppty_num = in_root_oppty_num;


GET DIAGNOSTICS out_rowupdate_count = ROW_COUNT;

END