from .engine import Job51Engine


if __name__ == "__main__":
    url = "https://search.51job.com/list/020000,000000,0000,00,9,99,{keywords},2,{pagenum}.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="
    job51 = Job51Engine(
        name='51job', 
        url=url,
        keywords='java%2520web',
        pagenum=1)
    job51.execute()
