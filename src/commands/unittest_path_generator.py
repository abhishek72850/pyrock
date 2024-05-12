import re
from typing import Optional, List, Tuple
from sublime import Region, View, FindFlags
from ..logger import Logger
from ..exceptions import InvalidTestFramework
from ..constants import PyRockConstants


logger = Logger(__name__)


# matches class name
CLASS_NAME_START_REGEX = r'^(?:class)\s+([a-zA-Z_0-9]\w*)\s*\((?:[^\)]*\):)?'
# matches test method with params
TEST_METHOD_FULL_REGEX = r'^\s*def\s+(test_[a-zA-Z_0-9]\w*)\s*\([^\)]*\):'
# matches class test method
CLASS_TEST_METHOD_FULL_REGEX = r'^(?: )+def\s+(test_[a-zA-Z_0-9]\w*)\s*\(\s*(?:cls|self)\s*,?[^\)]*\):'


class TestPathGenerator:
    @staticmethod
    def _get_django_test_path(
        relative_path: str,
        class_name: Optional[str] = None,
        method_name: Optional[str] = None,
    ) -> str:
        test_path = f"{relative_path.replace('.py', '').replace('/', '.')}"

        if class_name:
            test_path = f"{test_path}.{class_name}"

        if method_name:
            test_path = f"{test_path}.{method_name}"

        return test_path

    @staticmethod
    def _get_pytest_test_path(
        relative_path: str,
        class_name: Optional[str] = None,
        method_name: Optional[str] = None,
    ) -> str:
        test_path = relative_path

        if class_name:
            test_path = f"{test_path}::{class_name}"

        if method_name:
            test_path = f"{test_path}::{method_name}"

        return test_path


    @staticmethod
    def _get_test_path(
        testing_framework: str,
        relative_path: str,
        class_name: Optional[str] = None,
        method_name: Optional[str] = None,
    ) -> str:

        if testing_framework == PyRockConstants.DJANGO_TEST_FRAMEWORK:
            test_path = TestPathGenerator._get_django_test_path(
                relative_path=relative_path,
                class_name=class_name,
                method_name=method_name,
            )

        elif testing_framework == PyRockConstants.PYTEST_TEST_FRAMEWORK:
            test_path = TestPathGenerator._get_pytest_test_path(
                relative_path=relative_path,
                class_name=class_name,
                method_name=method_name,
            )
        else:
            raise InvalidTestFramework()

        return test_path

    @staticmethod
    def _get_class_and_its_method_name(
        view: View,
        full_line_region: Region
    ) -> Tuple[Optional[str], Optional[str]]:
        class_name = None
        method_name = None

        test_method_region: Region = view.find(
            pattern=TEST_METHOD_FULL_REGEX,
            start_pt=full_line_region.begin(),
            flags=FindFlags.IGNORECASE
        )

        test_method_text = view.substr(
            test_method_region
        )
        logger.debug(f"Full test method text: {test_method_text}")
        logger.debug(f"Test method region point: {test_method_region.to_tuple()}")

        class_test_function_matches = re.findall(
            CLASS_TEST_METHOD_FULL_REGEX,
            test_method_text,
            re.MULTILINE | re.DOTALL
        )

        # Check its a class test method
        if len(class_test_function_matches) > 0:
            # Its a class test methods
            method_name = class_test_function_matches[0]
            logger.debug(f"Class first test method name: {method_name}")

            # Find every class name region
            class_name_only_regex = r'^(?:class)\s+([a-zA-Z_0-9]\w*)(?:\([^\)]*\):|:)'

            matched_regions: List[Region] = view.find_all(
                pattern=class_name_only_regex,
                flags=FindFlags.IGNORECASE
            )
            logger.debug(f"Matched regions list: {matched_regions}")

            # Finding the matched test method belongs to which class
            # its done by first getting all the classes in that view
            # then check which class position is closest to that test method
            closest_class_region = None
            for region in matched_regions:
                logger.info(f"{view.substr(region)}, {region.to_tuple()}")

                if test_method_region.begin() > region.begin():
                    closest_class_region = region

            logger.debug(f"Closest class {view.substr(closest_class_region)}")
            if closest_class_region:
                match_result = re.match(
                    class_name_only_regex, view.substr(closest_class_region)
                )
                class_name = match_result.group(1)

        # Check its a individual test method
        elif test_function_match := re.match(
            TEST_METHOD_FULL_REGEX,
            test_method_text,
        ):
            # Its not a class method
            method_name = test_function_match.group(1)

        else:
            logger.debug(
                "Unable to identify whether its a class or non-class method"
            )

        return (class_name, method_name)

    @staticmethod
    def _generate_class_based_test_path(
        view: View,
        class_name: str,
        testing_framework: str,
        method_name: Optional[str] = None,
    ) -> Optional[str]:
        test_path: Optional[str] = None
        relative_path = None

        class_symbol_locations = view.window().symbol_locations(class_name)

        # Finding the relative path for self view
        for symbol_loc in class_symbol_locations:
            # symbol_loc.path has file name
            if symbol_loc.path == view.file_name():
                # symbol_loc.display_name has relative path
                relative_path = symbol_loc.display_name
                break

        if relative_path:
            test_path = TestPathGenerator._get_test_path(
                testing_framework=testing_framework,
                relative_path=relative_path,
                class_name=class_name,
                method_name=method_name,
            )
            logger.debug(f"class based test path: {test_path}")
        else:
            logger.debug("Could not resolve class relative path")

        return test_path

    @staticmethod
    def _generate_method_based_test_path(
        view: View,
        method_name: str,
        testing_framework: str,
    ):
        test_path: Optional[str] = None
        relative_path = None

        method_symbol_locations = view.window().symbol_locations(method_name)

        for symbol_loc in method_symbol_locations:
            if symbol_loc.path == view.file_name():
                relative_path = symbol_loc.display_name
                break

        if relative_path:
            test_path = TestPathGenerator._get_test_path(
                testing_framework=testing_framework,
                relative_path=relative_path,
                class_name=None,
                method_name=method_name,
            )
            logger.debug(f"method based test path: {test_path}")
        else:
            logger.debug("Could not resolve method relative path")

        return test_path

    @staticmethod
    def generate(region, view: View, testing_framework: str) -> Optional[str]:
        logger.debug(f"Testing framework {testing_framework}")

        full_line_region = view.full_line(region)
        full_line_text: Optional[str] = view.substr(full_line_region)
        logger.debug(f"Selected full line text: {full_line_text}")

        class_name = None
        method_name = None

        if class_match := re.match(CLASS_NAME_START_REGEX, full_line_text):
            # Its a class name
            class_name = class_match.group(1)

        # If its not class name now check
        # whether its class test method or indvidual test method
        if class_name is None:
            class_name, method_name = TestPathGenerator._get_class_and_its_method_name(
                view, full_line_region
            )

        logger.debug(
            f"Extracted class and test method name: {class_name} {method_name}"
        )

        test_path: Optional[str] = None

        if class_name:
            test_path = TestPathGenerator._generate_class_based_test_path(
                view,
                class_name,
                testing_framework,
                method_name,
            )
        elif method_name:
            test_path = TestPathGenerator._generate_method_based_test_path(
                view, method_name, testing_framework
            )
        else:
            logger.debug("Could not find class or method name to generate test path")

        logger.debug(f"Generated test path: {test_path}")

        return test_path
