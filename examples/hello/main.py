from java.lang import System  # type: ignore

System.out.println("Hello from JVM!")

print(f"Java Version: {System.getProperty('java.version')}")
print(f"Java Vendor: {System.getProperty('java.vendor')}")
print(f"Java Home: {System.getProperty('java.home')}")
print(f"OS Name: {System.getProperty('os.name')}")

print(f"Current classpath: {System.getProperty('java.class.path')}")

print("✅ JVM-PyBind example completed successfully!")
