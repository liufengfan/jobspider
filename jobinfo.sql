create database if not exists jobinfo default charset utf8;

use jobinfo;

create table if not exists jobinfo(
    jid varchar(32) primary key,    -- id
    jurl varchar(255),              -- 信息url地址
    jpost   varchar(255),           -- 岗位名称
    jsalary varchar(255),           -- 薪资
    jcompany varchar(255),          -- 公司
    jsummary varchar(255),          -- 摘要信息
    jpostinfo text,                 -- 岗位要求
    jconcatinfo varchar(255),       -- 联系方式
    jsource varchar(255)            -- 信息来源
);

