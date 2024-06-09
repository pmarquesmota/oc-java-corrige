FROM gradle:8.7-jdk21-alpine AS BUILDER

WORKDIR /app

COPY . .

RUN gradle bootWar

FROM tomcat:10.1.24-jre21-temurin-jammy

RUN rm -rf $CATALINA_HOME/webapps/*

COPY --from=BUILDER "/app/build/libs/*" "$CATALINA_HOME/webapps/ROOT.war"

EXPOSE 8080


