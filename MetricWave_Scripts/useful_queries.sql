-- Delete dataset_rows and datasets data and reset auto increment to 1
    DELETE FROM dataset_rows;
    ALTER TABLE dataset_rows AUTO_INCREMENT = 1;

    DELETE FROM datasets;
    ALTER TABLE datasets AUTO_INCREMENT = 1;


--