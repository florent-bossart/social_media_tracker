
    
    

with dbt_test__target as (

  select id as unique_field
  from `wagon-bootcamp-451201`.`dbt_fbossart_day2_advanced`.`my_second_dbt_model`
  where id is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


