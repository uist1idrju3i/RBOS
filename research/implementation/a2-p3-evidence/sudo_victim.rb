begin
  Privilege.sudo("fixture") do
    $victim_elevated = true
    sleep_ms 1000
  end
ensure
  $victim_ensured = true
end
