# project 1 DB 

-- Test
select * from cars;
select	distinct brand,
		count(*)
from cars
group by 1
order by 1;

select * from recalls;
select count(*) from recalls;	-- ex) 3927 without error. 


select	distinct brand,
		count(*)
from recalls
group by brand
order by 1;

select	count(distinct brand)
from	recalls;	-- ex) 91
