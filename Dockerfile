FROM amazoncorretto:21

WORKDIR /app

COPY build/libs/app.jar app.jar

EXPOSE 3011

ENTRYPOINT ["sh", "-c", "java -jar app.jar --spring.profiles.active=${SPRING_PROFILE}"]