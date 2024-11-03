#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_LINE_LENGTH 1024
#define MAX_URL_LENGTH 256
#define MAX_IP_LENGTH 16
#define MAX_ERROR_LENGTH 512

void get_current_timestamp(char *timestamp, size_t size) {
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    strftime(timestamp, size, "%Y%m%d_%H%M%S", tm_info);
}

void parse_access_log(const char *access_log_path, const char *output_file) {
    FILE *access_log = fopen(access_log_path, "r");
    if (!access_log) {
        perror("Error opening access log file");
        return;
    }

    FILE *output = fopen(output_file, "w");
    if (!output) {
        perror("Error creating output file for access log");
        fclose(access_log);
        return;
    }

    char line[MAX_LINE_LENGTH];
    char ip[MAX_IP_LENGTH];
    char timestamp[30];
    char url[MAX_URL_LENGTH];
    char status[4];
    char bytes[10];

    fprintf(output, "IP\tTimestamp\tURL\tStatus\tBytes\n");

    while (fgets(line, sizeof(line), access_log)) {
        if (sscanf(line, "%15s - - [%29[^]]] \"%*s %255s HTTP/%*s\" %3s %9s",
                   ip, timestamp, url, status, bytes) == 4) {
            fprintf(output, "%s\t%s\t%s\t%s\t%s\n", ip, timestamp, url, status, bytes);
        }
    }

    fclose(output);
    fclose(access_log);
}

void parse_error_log(const char *error_log_path, const char *output_file) {
    FILE *error_log = fopen(error_log_path, "r");
    if (!error_log) {
        perror("Error opening error log file");
        return;
    }

    FILE *output = fopen(output_file, "w");
    if (!output) {
        perror("Error creating output file for error log");
        fclose(error_log);
        return;
    }

    char line[MAX_LINE_LENGTH];
    char timestamp[30];
    char log_level[16];
    char ip[MAX_IP_LENGTH];
    char error_message[MAX_ERROR_LENGTH];

    fprintf(output, "Timestamp\tLog Level\tIP\tError Message\n");

    while (fgets(line, sizeof(line), error_log)) {
        if (sscanf(line, "[%29[^]] %15s] [client %15s] %[^\n]",
                   timestamp, log_level, ip, error_message) == 4) {
            fprintf(output, "%s\t%s\t%s\t%s\n", timestamp, log_level, ip, error_message);
        }
    }

    fclose(output);
    fclose(error_log);
}

int main() {
    const char *access_log_path = "/var/log/apache2/access.log";  // Change as needed
    const char *error_log_path = "/var/log/apache2/error.log";    // Change as needed

    char timestamp[20];
    get_current_timestamp(timestamp, sizeof(timestamp));

    char access_output_file[50];
    char error_output_file[50];
    
    snprintf(access_output_file, sizeof(access_output_file), "traffic_%s.txt", timestamp);
    snprintf(error_output_file, sizeof(error_output_file), "errors_%s.txt", timestamp);

    parse_access_log(access_log_path, access_output_file);
    parse_error_log(error_log_path, error_output_file);

    printf("Access data saved to %s\n", access_output_file);
    printf("Error data saved to %s\n", error_output_file);

    return 0;
}
