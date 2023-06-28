while true; do
    python3 main.py
    exit_code=$?

    if [[ $exit_code -eq 0 ]]; then
        # Successful execution, exit the loop
        break
    else
        # Error encountered, retry after a delay
        echo "Error occurred. Retrying..."
        sleep 1
    fi
done