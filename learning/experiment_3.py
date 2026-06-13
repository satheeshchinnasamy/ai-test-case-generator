def generate_prompt(user_story, number_cases=7, domain="general" ):
    return f"Generate {number_cases} test cases for this {domain} user story {user_story}"

print(generate_prompt("User login"))

print(generate_prompt("User wants login", domain="Insurance"))

print(generate_prompt("User wants login",domain="ecommerce", number_cases=10))