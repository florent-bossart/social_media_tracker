

  create or replace view `wagon-bootcamp-451201`.`dbt_fbossart_day2_advanced`.`my_second_dbt_model`
  OPTIONS()
  as -- Use the `ref` function to select from other models

select *
from `wagon-bootcamp-451201`.`dbt_fbossart_day2_advanced`.`my_first_dbt_model`
where id = 1;

