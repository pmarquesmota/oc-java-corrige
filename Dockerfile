FROM gradle:8.12.1-jdk-alpine AS BUILDER

WORKDIR /app

COPY . .

RUN gradle bootWar

FROM tomcat:alpine

RUN rm -rf $CATALINA_HOME/webapps/*

COPY --from=BUILDER "/app/build/libs/*" "$CATALINA_HOME/webapps/ROOT.war"

EXPOSE 8080


