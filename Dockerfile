FROM gradle:8.12.1-jdk-alpine AS BUILDER
COPY . .
RUN --mount=type=cache,target=/home/gradle/.gradle gradle bootWar

FROM tomcat:alpine
RUN rm -rf $CATALINA_HOME/webapps/*
COPY --from=BUILDER "/home/gradle/build/libs/*" "$CATALINA_HOME/webapps/ROOT.war"
EXPOSE 8080
