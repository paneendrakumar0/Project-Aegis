from setuptools import setup

package_name = "aegis_ros_bridge"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Project Aegis",
    maintainer_email="maintainer@example.com",
    description="Replay Project Aegis telemetry into ROS 2 topics.",
    license="Proprietary",
    entry_points={
        "console_scripts": [
            "telemetry_replay_node = aegis_ros_bridge.telemetry_replay_node:main",
        ],
    },
)

