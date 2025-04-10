# project 1 DB 

-- Test 
delete from recalls;
delete from engine_specs;
delete from ev_specs;
delete from cars;
select * from cars;

select distinct brand from recalls
order by 1;
where brand like '%포드%';

select * from recalls
where brand like '%토요%';
and name like '%EV%';