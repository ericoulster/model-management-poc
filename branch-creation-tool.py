from github import Github
import json

from github import Auth


import pandas as pd
from io import StringIO


def product_picker(df, product):
    df = df.set_index('Product')
    product_name = df[df.index == 'Product Y'].T
    product_name = product_name[product_name['Product Y'] == 0]
    products_to_delete = product_name.index.values.tolist()
    return products_to_delete

# You have to put your access token in the path for this to work. Do not upload your access token.
with open("access_token.json") as file:
    key = json.load(file)

auth = Auth.Token(key["key"])

g = Github(auth=auth)

repo = g.get_user().get_repo('model-management-poc')


def branch_set_up(company_name, product):
    branch_name = company_name + '_' + product
    branch_name = branch_name.replace(' ', '')

    # getting dependency matrix
    dep_mat = repo.get_contents('dependency-matrix.csv', ref='build')
    # Reading in the dependency matrix from github, then parsing the file
    dep_mat_main = StringIO(dep_mat.decoded_content.decode())
    df = pd.read_csv(dep_mat_main)

    to_delete = product_picker(df, product)
    
    source_branch = repo.get_branch('build')

    # Error-handling for PyGithub is currently sufficient so as to skip the "scan if branch exists" check. I would add this later.
    repo.create_git_ref(ref='refs/heads/' + branch_name, sha=source_branch.commit.sha)
    
    # deleting the dependency matrix in new branch
    dep_mat = repo.get_contents('dependency-matrix.csv', ref=branch_name)
    repo.delete_file(dep_mat.path, f"removed dependency matrix", branch=branch_name, sha=dep_mat.sha)

    # iteratively deletes all objects within a model folder
    for i in to_delete:
        contents = repo.get_contents(i, ref=branch_name)
        for j in contents:
            repo.delete_file(j.path, f"removed {j.path}", branch=branch_name, sha=j.sha)

# This function was used to create the 'Computech_ProductZ' branch. 
# You may either call the above function below, or import into another .py/ipynb file to run.

if __name__ == "__main__":
    branch_set_up(input("Select Company Name:"), input("Select Product:"))