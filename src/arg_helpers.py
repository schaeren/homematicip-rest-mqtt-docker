import sys
import logging
import argparse
from pathlib import Path

import os

class CmdLineParser:

    def _get_arg_str(self, arg, env_var_name, default):
        if arg is not None:
            return arg # arg is already a string (from argparse)
        env_var = os.getenv(env_var_name)
        if env_var is not None:
            return env_var
        return default

    def _get_arg_int(self, arg, env_var_name, default):
        if isinstance(arg, int):
            return arg
        env_val = os.getenv(env_var_name)
        if env_val is not None:
            try:
                return int(env_val)
            except ValueError:
                pass  # ignore invalid int in environment
        return default

    def _get_arg_bool(self, arg, env_var_name, default):
        true_values = {'true', '1', 'yes', 'on'}
        if isinstance(arg, bool):
            return arg
        if isinstance(arg, str):
            return arg.lower() in true_values
        env_val = os.getenv(env_var_name)
        if isinstance(env_val, str):
            return env_val.lower() in true_values
        return default
    
    def _get_arg_pwd(self, arg, env_var_name, default):
        if arg is not None:
            return arg # arg is already a string (from argparse)
        env_var = os.getenv(env_var_name)
        if env_var is not None:
            return env_var
        file_env_var = os.getenv(env_var_name + "_FILE")
        if file_env_var is not None:
            try:
                pwdFile = self._makePathAbsolute(file_env_var)
                with open(pwdFile, 'r') as f:
                    return f.read().strip()
            except IOError:
                raise ValueError(f"Could not read password from file: {pwdFile}")
        return default
    
    def _makePathAbsolute(self, path):
        if path is None:
            return None
        if not Path(path).is_absolute():
            working_dir = os.getcwd()
            return os.path.join(working_dir, path)
        return path

    def __init__(self):
        self.__logger = logging.getLogger("hmip2mqtt")
        _default_logging_config_file = "/config/logging.ini"

        parser = argparse.ArgumentParser()
        parser.add_argument('--hmip_config_file', '--config', help="Path to the config file used to access the Homematic IP cloud, default: -")
        parser.add_argument('--server', help="Hostname od IP address of the MQTT broker, default: localhost")
        parser.add_argument('--port', type=int, help="Port number of the MQTT broker, default: 1883")
        parser.add_argument('--username', help="Username for the MQTT broker, default: none")
        parser.add_argument('--password', help="Password for the MQTT broker, default: none")
        parser.add_argument('--ca_cert_file', help="Abolute or relative path to the CA certificate file, default: none")
        parser.add_argument('--client_cert_file', help="Abolute or relative path to the client certificate file, default: none")
        parser.add_argument('--client_key_file', help="Abolute or relative path to the client private key file, default: none")
        parser.add_argument('--use_tls', help="Use TSL for the MQTT connection, true/false, default: true if port number is not 1880 else false")
        parser.add_argument('--disable_server_cert', help="Disable server certificate verification (if TLS is enabled), true/false, default: false")
        parser.add_argument('--no_publish', help="Don't actually publish messages (log only), true/false, default: false")
        args = parser.parse_args()

        # Set the attributes based on the parsed arguments or environment variables
        self.hmip_config_file    = self._get_arg_str(  args.hmip_config_file,     "HMIP_CONFIG_FILE",         "")
        self.server              = self._get_arg_str(  args.server,               "MQTT_SERVER",              "localhost")
        self.port                = self._get_arg_int(  args.port,                 "MQTT_PORT",                1883)
        self.username            = self._get_arg_str(  args.username,             "MQTT_USERNAME",            None)
        self.password            = self._get_arg_pwd(  args.password,             "MQTT_PASSWORD",            None)
        self.ca_cert_file        = self._get_arg_str(  args.ca_cert_file,         "MQTT_CA_CERT_FILE",        None)
        self.client_cert_file    = self._get_arg_str(  args.client_cert_file,     "MQTT_CLIENT_CERT_FILE",    None)
        self.client_key_file     = self._get_arg_str(  args.client_key_file,      "MQTT_CLIENT_KEY_FILE",     None)
        self.use_tls             = self._get_arg_bool( args.use_tls,              "MQTT_USE_TLS",             self.port != 1883)
        self.disable_server_cert = self._get_arg_bool( args.disable_server_cert,  "MQTT_DISABLE_SERVER_CERT", False)
        self.no_publish          = self._get_arg_bool( args.no_publish,           "MQTT_NO_PUBLISH",          False)

        self.__logger.info(f"Start parameters:")
        self.__logger.info(f"  --hmip_config_file: {self.hmip_config_file}")
        self.__logger.info(f"  --server: {self.server}")
        self.__logger.info(f"  --port: {self.port}")
        self.__logger.info(f"  --username: {self.username if self.username else '<not set>'}")
        self.__logger.info(f"  --password: {'<set>' if self.password else '<not set>'}")
        self.__logger.info(f"  --ca_cert_file: {self.ca_cert_file if self.ca_cert_file else '<not set>'}")
        self.__logger.info(f"  --client_cert_file: {self.client_cert_file if self.client_cert_file else '<not set>'}")
        self.__logger.info(f"  --client_key_file: {self.client_key_file if self.client_key_file else '<not set>'}")
        self.__logger.info(f"  --use_tls: {self.use_tls}")
        self.__logger.info(f"  --disable_server_cert: {self.disable_server_cert}")
        self.__logger.info(f"  --no_publish: {self.no_publish}")

        # Validate some arguments

        # check --hmip_config_file
        if self.hmip_config_file:
            self.hmip_config_file = self._makePathAbsolute(self.hmip_config_file)
            if not os.path.isfile(self.hmip_config_file):
                self.__logger.error(f"Config file with HomematicIP access token not found: {self.hmip_config_file}")
                sys.exit(1)
                # raise ValueError(f"Config file does not exist: {self.hmip_config_file}")

        if self.use_tls:

            if self.disable_server_cert:
                self.__logger.warning("Server certificate verification is disabled. This is not recommended for production use.")
            else:
                # check --ca_cert_file
                if not self.ca_cert_file:
                    self.__logger.error(f"--ca_cert_file OR $MQTT_CA_CERT_FILE file must be provided if using TLS")
                    sys.exit(1)
                self.ca_cert_file = self._makePathAbsolute(self.ca_cert_file)
                if not self.ca_cert_file or not os.path.isfile(self.ca_cert_file):
                    self.__logger.error(f"CA certificate file does not exist: {self.ca_cert_file}")
                    sys.exit(1)
            
            if self.client_cert_file or self.client_key_file:

                # check --client_cert_file
                if self.client_cert_file is None:
                    self.__logger.error(f"--client_cert_file or $MQTT_CLIENT_CERT_FILE must not be empty if client certificate is used")
                    sys.exit(1)
                self.client_cert_file = self._makePathAbsolute(self.client_cert_file)
                if not self.client_cert_file or not os.path.isfile(self.client_cert_file):
                    self.__logger.error(f"Client certificate file does not exist: {self.client_cert_file}")
                    sys.exit(1)
                
                # check --client_key_file
                if self.client_key_file is None:
                    self.__logger.error(f"--client_key_file or $MQTT_CLIENT_KEY_FILE) must not be empty if client certificate is used")
                    sys.exit(1)
                self.client_key_file = self._makePathAbsolute(self.client_key_file)
                if not self.client_key_file or not os.path.isfile(self.client_key_file):
                    self.__logger.error(f"Client key file does not exist: {self.client_key_file}")
                    sys.exit(1)
