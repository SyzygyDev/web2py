#!/usr/bin/env python
# coding: utf8
from gluon import *

class AccountAdmin:
    def __init__(self, db):
        self.db = db
    
    def get_account(self, userID, sessionRole=4):
        account = False
        if userID:
            query = self.db.auth_user.id == userID
            result = self.db(query).select().first()
            if result:
                account = self._extract_account(result, sessionRole)
            
        return account
    
    def get_accounts(self, sessionRole=4):
        accounts = False
        results = self.db(self.db.auth_user.id > 0).select() 
        for result in results:
            account = self._extract_account(result, sessionRole)
            if account:
                if not accounts:
                    accounts = []
                accounts.append(account)
            
        return accounts
    
    def create_account(self, auth, firstName, lastName, email, password):
        # Cade TODO: self.db.auth_user.password.requires[0](password)[0] ~ CRYPT(digest_alg='pbkdf2(1000,20,sha512)', salt=True)(password)[0]
        id = self.db.auth_user.insert(first_name=firstName, last_name=lastName, email=email,
            password=self.db.auth_user.password.requires[0](password)[0]) 
        auth.add_membership('Staff', id)
            
        return id
    
    def check_password(self, password):
        # Determine if the supplied password matches the password for the admin account
        if self.db.auth_user.password.validate(password) == (self.db(self.db.auth_user.id==self.userID).select().first().password, None):
            return True
        else:
            return False
            
    
    def email_exists(self, email):
        query = self.db.auth_user.email == email
        if self.db(query).count():
            return True
        else:
            return False
    
    
    def update_account(self, userID, firstName, lastName, email):
        if not userID:
            return False
        query = self.db.auth_user.id == userID
        self.db(query).update(first_name=firstName, last_name=lastName, email=email)
        return True
            
            
    def update_password(self, password):
        query = self.db.auth_user.id == self.userID
        self.db(query).update(password=self.db.auth_user.password.requires[0](password)[0])
        return True
       
    def set_organization_administrator(self, userID=''):
        # Add the given user account to the 'Administrator' group
        # This will allow the user to edit organization campaigns, activities, applications, etc.
        if not userID:
            userID = self.userID
        
        self.db.auth_membership.update_or_insert(user_id=userID, group_id=self.adminGroup)

    def get_group_memberships(self, userID):
        groups = False
        if userID:
        
            groups = []

            query = (self.db.auth_membership.user_id == userID) & (self.db.auth_membership.group_id == self.db.auth_group.id)
            results = self.db(query).select(self.db.auth_membership.group_id, self.db.auth_group.role)

            for result in results:
                groups.append(result.auth_membership.group_id)

        return groups

    def update_group_memberships(self, groupIDs, userID):
        if userID:
            # Delete any existing membeships for the user
            self.delete_group_memberships(userID)
            # Create a new membership for each group ID
            for groupID in groupIDs:
                self.db.auth_membership.insert(user_id=userID, group_id=groupID)

    def delete_group_memberships(self, userID):
        if userID:

            query = self.db.auth_membership.user_id == userID
            self.db(query).delete()

    def get_available_groups(self):
        groups = []

        query = self.db.auth_group.id > 0
        results = self.db(query).select()

        for result in results:
            groups.append({'groupID': result.id, 'groupName': result.role})

        return groups
    
    def _extract_account(self, account, sessionRole):
        thisAccount = False
        membershipExceeded = False
        query = self.db.auth_membership.user_id == account.id
        memberships = self.db(query).select()
        if memberships:
            for membership in memberships:
                if membership.group_id < sessionRole:
                    membershipExceeded = True

        if not membershipExceeded:
            thisAccount = {}
            thisAccount['userID'] = account.id
            thisAccount['fname'] = account.first_name
            thisAccount['lname'] = account.last_name
            thisAccount['email'] = account.email

        return thisAccount
