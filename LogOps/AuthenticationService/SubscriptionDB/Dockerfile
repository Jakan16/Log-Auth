FROM mysql:8.0.13
ENV MYSQL_ROOT_PASSWORD 123456
ENV MYSQL_ROOT_HOST %
ENV MYSQL_DATABASE SubscriptionDB
ENV MYSQL_USER my_sql_user
ENV MYSQL_PASSWORD my_sql_password
COPY my.cnf /etc/mysql/
EXPOSE 3306
COPY initSql.sql /docker-entrypoint-initdb.d