from botocore.retries.standard import MaxAttemptsChecker
from .db import dynamodbResource, dynamodbClient,s3_Resource 
from email_service import settings
import uuid
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from datetime import datetime


ENVIRONMENT=settings.ENVIRONMENT



if ENVIRONMENT== "dev":
    ENVIRONMENT="Dev"


if ENVIRONMENT== "prod":
    ENVIRONMENT="Prod"

if ENVIRONMENT=="qa":
    ENVIRONMENT="QA"

if ENVIRONMENT=="demo":
    ENVIRONMENT="Demo"
    
# CODE BELOW

class BaseTable:
    table_name = "TABLE"
    table_prefix = "BASE"
    table_fields = []

    def __init__(self):
        _tableName = "_".join([ENVIRONMENT, self.table_name])
        self.dbresource = dynamodbResource
        self.dbclient = dynamodbClient
        self.table = self.dbresource.Table(_tableName)
        if self.table_prefix == "BASE":
            raise AttributeError("table_prefix cannot be blank or BASE")
        if not isinstance(self.table_fields, list) or len(self.table_fields) == 0:
            raise AttributeError("table manadatory fields are not available, should be in a list")

        self.__class__.table_name = _tableName

    

    @property
    def object_id(self):
        epoch = datetime.utcfromtimestamp(0)
        timestamp = str((datetime.today() - epoch).total_seconds() * 1000.0).split('.')[0]
        return "".join([self.table_prefix, timestamp,uuid.uuid4().hex[:10]]).upper()

    def audits(self, request_type, user):
        if request_type not in {"C", "U", "D"}:
            raise AttributeError(f"request type should be only 'C' 'U' 'D'")
        request_types = {
            "C": ["createdBy", "createdAt"],
            "U": ["updatedBy", "updatedAt"],
            "D": ["deletedBy", "deletedAt"]
        }

        audit = {
            "tenant": 0,
            "isActive": True if request_type != "D" else False,
        }
        by, at = request_types[request_type]       
        audit[by] = user
        audit[at] = datetime.today().strftime("%s")
        return audit

    def table_fields(self):
        pass

    def get_item(self, **kwargs):
        pkeys = list(map(lambda o : o["AttributeName"], self.table.key_schema))
        data = {}
        for key in pkeys:
            if key not in kwargs.keys():
                raise AttributeError(f"{key} is mandatory field for fetch item detail")
            data[key] = kwargs.get(key)
        try:
            response = self.table.get_item(Key=data)
            return response["Item"]
        except Exception as e:
            return str(e)


class CommunicationTemplate(BaseTable):
    table_name = "CommunicationTemplate"
    table_prefix = "CNTML"
    table_fields = ["entityId","entityType","subject","templateLanguage","templateCategory",
                            "templateName","templateURL","templateURLCDN","createdBy"]

    def _table_fields(self):
        return self.table_fields

    def create_template(self, **kwargs):
        """Created communication template"""
        
        templateName=kwargs.get("templateName")
        templateLanguage=kwargs.get("templateLanguage")
        templateCategory = kwargs.get("templateCategory")
        entity_id=kwargs.get('entityId')
        programId=kwargs.get('programId')
        
        if templateCategory  in ["Private","Base"]:
            entity_id=settings.entityId

       
        
        if programId == None:
            response= self.table.query(
                    IndexName="templateName-templateId-index",
                    KeyConditionExpression=Key("templateName").eq(templateName),
                    FilterExpression=Key("entityId").eq(entity_id) & Key("isActive").eq(True) & Key("communicationType").eq("E")  & Key("templateLanguage").eq(templateLanguage)
                )
        
        if programId !=None:
            self.table.query(
                    IndexName="entityId-templateId-index",
                    KeyConditionExpression=Key("entityId").eq(entity_id),
                    FilterExpression=Key("templateName").eq(templateName)  & Key("isActive").eq(True) & Key("communicationType").eq("E")  & Key("templateLanguage").eq(templateLanguage) & Key("programId").eq(programId)
                )
                
        data=response.get('Items')
        
        if  data == []:

            template_id = self.object_id
            audits = self.audits("C", kwargs.get("email"))
            mandatory_fields = self._table_fields()
            data = {
                "templateId": template_id,
                "compositeKey": "-".join([self.table_prefix, template_id]),
                **audits
            }
            for field in mandatory_fields:
                if field not in kwargs.keys():
                    raise AttributeError(f"{field} field missing")
                data[field] = kwargs.get(field)

            data["communicationType"] = "E"
            data['entityId'] = entity_id
            if 'programId' not in data and data['templateCategory']== 'Local':
                data['programId'] = programId
            
           
            
           
            return self.table.put_item(Item=data)
        else:
            raise AttributeError('Template Already existed')
    
    def create_templateLocal(self, **kwargs):

        
        """Copy Base template to local"""
        templateName=kwargs.get("templateName")
        templateLanguage=kwargs.get("templateLanguage")
        templateCategory = kwargs.get("templateCategory")
        entity_id=kwargs.get('entityId')
        programId=kwargs.get('programId')
        response = self.table.query(
                    IndexName="entityId-templateId-index",
                    KeyConditionExpression=Key("entityId").eq(entity_id) ,
                    FilterExpression=Key("templateName").eq(templateName) & Key("isActive").eq(True) & Key("communicationType").eq("E")  & Key("templateLanguage").eq(templateLanguage) & Key("programId").eq(programId)
                )
        data=response.get('Items')
        if  data == []:
            template_id = self.object_id
            audits = self.audits("C", kwargs.get("email"))
            mandatory_fields = self._table_fields()
            data = {
                "templateId": template_id,
                "compositeKey": "-".join([self.table_prefix, template_id]),
                **audits
            }
            for field in mandatory_fields:
                if field not in kwargs.keys():
                    raise AttributeError(f"{field} field missing")
                data[field] = kwargs.get(field)
            data["communicationType"] = "E"
            data['entityId'] = entity_id
            if 'programId' not in data and data['templateCategory']== 'Local':
               data['programId'] = programId    
            return self.table.put_item(Item=data)
        else:
            return False

    def get_templates(self, entity_id=None):
    
        
       

       

        """return templates by entity_id"""
        if not entity_id:
            raise AttributeError("please provide entity_id")
        if entity_id:
            index = "entityId-templateId-index"
            key = "entityId"
            value = entity_id
        
        responseBaseTemplates = self.table.query(
            IndexName="entityId-templateId-index",
            KeyConditionExpression=Key(key).eq(value),
            FilterExpression=Key("isActive").eq(True) & Key("communicationType").eq("E") & Key("templateCategory").eq("Base") 
            )
        responsePrivateTemplates= self.table.query(
            IndexName="entityId-templateId-index",
            KeyConditionExpression=Key(key).eq(value),
            FilterExpression=Key("isActive").eq(True) & Key("communicationType").eq("E") & Key("templateCategory").eq("Private") 
            )
        data={}
        data['Private']=responsePrivateTemplates.get('Items')
        data['Base']=responseBaseTemplates.get('Items')
    
        return data
    
    def get_templates_1(self, entity_id=None):
    
        
        entity_id=int(entity_id)

       

        """return templates by entity_id"""
        if not entity_id:
            raise AttributeError("please provide entity_id")
        if entity_id:
            index = "entityId-templateId-index"
            key = "entityId"
            value = entity_id
        
        responseBaseTemplates = self.table.scan(
           
            FilterExpression=Key('entityId').eq(90112) & Key("communicationType").eq("E") & Key("templateCategory").eq("Base") 
            )
        responsePrivateTemplates= self.table.scan(
            FilterExpression=Key('entityId').eq(value) & Key("communicationType").eq("E") & Key("templateCategory").eq("Private") 
            )
        data={}
        data['Private']=responsePrivateTemplates.get('Items')
        data['Base']=responseBaseTemplates.get('Items')

        return data
    
    def get_templates_hub_transfer(self, entity_id=None):

        """return templates by entity_id"""
        if not entity_id:
            raise AttributeError("please provide entity_id")
        if entity_id:
            index = "entityId-templateId-index"
            key = "entityId"
            value = entity_id
        
        responseBaseTemplates = self.table.query(
            IndexName="entityId-templateId-index",
            KeyConditionExpression=Key(key).eq(value),
            FilterExpression=Key("isActive").eq(True) & Key("communicationType").eq("E") & Key("templateCategory").eq("Base") 
            )
        data={}
        data['Base']=responseBaseTemplates.get('Items')
        return data
    
    def get_templateshublocal(self, entity_id=None,programId=None):

        """return templates by entity_id and programId"""
        if  not any([programId, entity_id]):
            raise AttributeError("please provide entity_id")
        response = self.table.query(
            IndexName="entityId-templateId-index",
            KeyConditionExpression=Key('entityId').eq(entity_id),
            FilterExpression= Key('programId').eq(programId) & Key("isActive").eq(True) & Key("communicationType").eq("E") & Key("templateCategory").eq("Local") 
            )
        return response.get("Items")

    def get_templatehublocal(self, entity_id=None,programId=None,templateId=None):
        """return template by entity_id and programId and templateId """
        if  not any([programId, entity_id,templateId]):
            raise AttributeError("please provide entity_id,programId,templateId")
        response = self.table.query(
            IndexName="entityId-templateId-index",
            KeyConditionExpression=Key('entityId').eq(entity_id),
            FilterExpression=Key('programId').eq(programId) &  Key('templateId').eq(templateId) & Key("isActive").eq(True) & Key("communicationType").eq("E") & Key("templateCategory").eq("Local") 
            )
        if response.get('Items') != []:
            return response.get("Items")[0]
        else:
            raise AttributeError("No such templateId found")
    
    def get_template(self, templateId=None, entity_id=None):
        """return templates by entity_id or templateId"""
        if not any([templateId, entity_id]):
            raise AttributeError("please provide atleast once parameter from templateId or entity_id")
        print(templateId,entity_id)
       
            
        response = self.table.query(
            IndexName="entityId-templateId-index",
            KeyConditionExpression=Key('entityId').eq(entity_id),
            FilterExpression= Key("templateId").eq(templateId)  & Key("isActive").eq(True) & Key("communicationType").eq("E")
            )
        return response.get("Items")

    
    def istemplate(self, templateName, entity_id,programId):
        print(templateName)
        print(programId)
        print(entity_id)
        """return bool if template availabel in the database"""

        response = self.table.query(
            IndexName="entityId-templateId-index",
            KeyConditionExpression=Key('entityId').eq(entity_id),
            FilterExpression=Key("templateName").eq(templateName) & Key("communicationType").eq("E") &Key("programId").eq(programId))
        print(response.get("Items"))

        if response.get("Items") !=[] :
            print(response.get("Items"))
            return True
        
        else:
            return False
        return False
    
    def isTemplate(self, templateName):
        """return bool if template available in the database"""
        response = self.table.query(
            IndexName="templateName-templateId-index",
            KeyConditionExpression=Key("templateName").eq(templateName),
            FilterExpression=Key("communicationType").eq("E") )
        if response.get("Items") !=[]:
            return True
        else:
            return False
        return False
    
    def delete_template(self, deleted_by, template_id):
        """delete template by id"""
        response = self.table.get_item(Key={'templateId':template_id})
        
        if 'Item' in response:

            if (response['Item']['isActive'] == False) and (response['Item']['communicationType']== 'E'):
               raise AttributeError("template is already deleted by "+str(response['Item']['deletedBy']+" "))
            
            elif (response['Item']['communicationType']=='S') or (response['Item']['communicationType']=='W'):
                raise AttributeError("This is not a Email Template")
            
            elif (response['Item']['isActive'] == True) and (response['Item']['communicationType']== 'E'):
                audits = self.audits("D", deleted_by)
                expr = []
                for number, key in dict(enumerate(audits.keys())).items():
                    new_key = f":var{number}"
                    expr.append(f" {key} = {new_key}")
                    audits[new_key] = audits[key]
                    del audits[key]
                update_expr = "SET" + ",".join(expr)
                return self.table.update_item(
                    Key={
                        "templateId": template_id
                    },
                    UpdateExpression=update_expr,
                    ExpressionAttributeValues={
                        **audits
                    }
                    )
        else:
            raise AttributeError("template not valid")  

    def update_template(self, template_id,a,v):
        """update template attribute using template id""" 
        return self.table.update_item(
                Key={'templateId':template_id},
                UpdateExpression=a,ExpressionAttributeValues=dict(v))    


class Program(BaseTable):
    table_name = "Program"
    table_prefix = "PRGM"
    table_fields = ["administratingOrganization","programType","entityStatus","programId"]

    def _table_fields(self):
        return self.table_fields

    def isProgram(self,programId):
        response = self.table.query(KeyConditionExpression=Key("programId").eq(programId))
        if response.get("Items") !=[]:
            print("2we")
            data=response.get('Items')
            print(data,'data')
            entityId=data[0]['organizationId']
            print(entityId)
            return True
        else:
            return False
    
    def getProgramentityId(self,programId):
        response = self.table.query(KeyConditionExpression=Key("programId").eq(programId))
        if response.get("Items") !=[]:
            data=response.get('Items')
            entityId=data[0]['organizationId']
            print(entityId)
            return entityId
        else:
            return False

class userTable(BaseTable):
    table_name = "User"
    table_prefix = "USR"
    table_fields = ["userId"]

    def _table_fields(self):
        return self.table_fields

    def isUser(self,createdBy):
        response = self.table.query(KeyConditionExpression=Key("userId").eq(createdBy))
        if response.get("Items") !=[]:
            
            return True
        else:
            raise AttributeError("you are not allowded to create/update Templates")

results=[]




class emailLogs(BaseTable):
    table_name = "EmailLogs"
    table_prefix = "MAIL"
    table_fields = ["subject", "email",'replyTo', "entityStatus","reason", "sentIn","templateName",'templateCategory','organizationId','programId','batchId','sessionId','language','userLocation','deletedBy','entityType','isActive','createdAt','createdBy','updatedAt', 'updatedBy', 'deletedAt','syncAt', 'syncVersion']
    
    
    def _table_fields(self):
        return self.table_fields
    
    
       
    def create_logs(self, **kwargs):
        """Created email logs"""
        
        logId = self.object_id
       
        
        
        
        mandatory_fields = self._table_fields()
        
        data = {
            "logId":logId,
            'createdBy':'ED',
            'deletedBy':'ED',
            'updatedBy':'ED',
            'syncVersion':1,
            'reason':None,
            "compositeKey":logId
        }
    
        for field in mandatory_fields:
            if field not in kwargs.keys():
                raise AttributeError(f"{field} field missing")
            data[field] = kwargs.get(field)
        self.table.put_item(Item=data)
        return data
    


   
    


    



    def BounceMails(self):
        
        response = self.table.scan(FilterExpression=Key("entityStatus").eq("Bounce") & Key('BounceBack').eq('N') & Key('templateName').eq('program-invitation'))
        data=response.get("Items")
        return data
    
    def BounceMailsprogram(self,programId,sentOn):
        response = self.table.scan(FilterExpression=Key("programId").eq(programId) & Key("entityStatus").eq("Bounce") & Key('BounceBack').eq('N') & Key("sentOn").eq(sentOn) & Key('templateName').eq('program-invitation'))
        data=response.get("Items")

        return data

    def totalMailsSentOnProgramInvitation(self,programId,sentOn):
         
        response = self.table.scan(FilterExpression=Key("programId").eq(programId) & Key("sentOn").eq(sentOn) &  Key('templateName').eq('program-invitation'))
        data=response.get("Items")

        return data
    


    def update_logs(self,logId):

             
        epoch = datetime.utcfromtimestamp(0)
        print(datetime.utcnow())
        timestamp = str((datetime.utcnow()- epoch).total_seconds() * 1000.0).split('.')[0]
        """update template attribute using template id""" 
        return self.table.update_item(

                Key={'logId':logId},
                UpdateExpression="set  BounceBack = :BounceBack, updatedAt=:updatedAt,syncAt=:syncAt", ExpressionAttributeValues={':BounceBack':'Y',':updatedAt':int(timestamp),':syncAt':int(timestamp)})    
        

       



    
    