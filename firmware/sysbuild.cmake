if(SB_CONFIG_RBOS_RELEASE)
  set(key "${SB_CONFIG_BM_BOOTLOADER_MCUBOOT_SIGNATURE_KEY_FILE}")
  if(NOT IS_ABSOLUTE "${key}" OR NOT EXISTS "${key}" OR IS_DIRECTORY "${key}")
    message(FATAL_ERROR "RBOS release requires an existing absolute signing key file outside the repository.")
  endif()
  file(REAL_PATH "${key}" key_real)
  file(REAL_PATH "${CMAKE_CURRENT_LIST_DIR}/.." repo_real)
  cmake_path(IS_PREFIX repo_real "${key_real}" NORMALIZE in_repo)
  if(in_repo)
    message(FATAL_ERROR "RBOS release rejects signing keys inside the repository.")
  endif()

  set(imgtool "${ZEPHYR_MCUBOOT_MODULE_DIR}/scripts/imgtool.py")
  function(rbos_get_public_key key_file output_var)
    execute_process(
      COMMAND "${Python3_EXECUTABLE}" "${imgtool}" getpub -k "${key_file}" -e pem
      RESULT_VARIABLE result
      OUTPUT_VARIABLE public_key
      ERROR_VARIABLE error
      OUTPUT_STRIP_TRAILING_WHITESPACE
      TIMEOUT 30
    )
    if(NOT "${result}" STREQUAL "0" OR public_key STREQUAL "")
      message(FATAL_ERROR "RBOS release cannot derive a public key with MCUboot imgtool: ${result}\n${error}")
    endif()
    set(${output_var} "${public_key}" PARENT_SCOPE)
  endfunction()

  rbos_get_public_key("${key_real}" release_public_key)
  file(GLOB default_keys "${ZEPHYR_MCUBOOT_MODULE_DIR}/root-*.pem")
  if(NOT default_keys)
    message(FATAL_ERROR "RBOS release cannot find MCUboot default keys for public-key comparison.")
  endif()
  foreach(default_key IN LISTS default_keys)
    rbos_get_public_key("${default_key}" default_public_key)
    if(release_public_key STREQUAL default_public_key)
      message(FATAL_ERROR "RBOS release rejects a signing key matching an MCUboot default public key.")
    endif()
  endforeach()
endif()
