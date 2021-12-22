import re
import logging
from fastapi import File
import pandas as pd
from fastapi import HTTPException
from pandas.core.frame import DataFrame

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
logger = logging.getLogger(__name__)

class SpreadsheetUtil:

    file = File('students.xlsx')

    def validate_email(self,email:str):
        if(re.fullmatch(regex, email)):
            return True
        return False
    

    def validate_file(self):
        extension = self.file.content_type
        if extension not in ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            logger.debug(
                "Unprocessable file format, file_type:{} . It should be a spreadsheet (.csv/.xlsx)  ".format(extension))
            raise HTTPException(
                status_code=422, detail='Uploaded file is not a spreadsheet')
        return True
    
    async def extract_spreadsheet_data(self):
        logger.debug("Extracting data from the spreadsheet")
        extension = self.file.content_type
        data = await self.file.read()
        try:
            if extension == 'text/csv':
                student_data = pd.read_csv(data)
            else:
                student_data = pd.read_excel(data)
        except Exception as e:
            logger.debug("Following Exception occured while extracting data : "+e)
            raise HTTPException(
                status_code=422, detail='Something went wrong while parsing the spreadsheet')

        if len(student_data) > 200:

            logger.debug("Not able to process more than 200 entries at once")
            raise HTTPException(
                status_code=422, detail='You can add only 200 students at once.')

        return student_data

    

    def validate_columns(self,student_data : DataFrame):
    
        for col in student_data.columns:
            student_data.rename({col: col.strip()}, axis=1, inplace=True)

        Invalid_columns = []
        if 'First name' not in student_data:
            Invalid_columns.append('First name')
        if 'Last name' not in student_data:
            Invalid_columns.append('Last name')
        if 'Email' not in student_data:
            Invalid_columns.append('Email')
        if 'Parent email' not in student_data:
            Invalid_columns.append('Parent email')
        if 'Password' not in student_data:
            Invalid_columns.append('Password')

        if len(Invalid_columns) > 0:
            detail = {
                'parse_error': 'Some columns were not found in the uploaded spreadsheet',
                'missing_columns': Invalid_columns
            }

            logger.debug(
                "Not able to parse the spreadsheet. Detail : {}".format(detail))
            raise HTTPException(status_code=422, detail=detail)

        return True


    def validate_data(self,student_data : DataFrame):
        valid_students = []
        email_list = []
        for index, student in student_data.iterrows():

            student['First name'] = str(student['First name']).strip()
            student['Last name'] = str(student['Last name']).strip()
            student['Email'] = str(student['Email']).strip()
            student['Password'] = str(student['Password']).strip()
            student['Parent email'] = str(student['Parent email']).strip()

            if str(student['First name']) != "nan" and str(student['Last name']) != "nan" and str(student['Email']) != "nan" and self.validate_email(email = student['Email']):
                
                if str(student['Email']) in email_list:

                    logger.debug('Duplicate entries found for this email - {}'.format(str(student['Email'])))
                    raise HTTPException(
                        status_code=422, detail='Duplicate entries found for this email - {}'.format(str(student['Email'])))

                email_list.append(str(student['Email']))
                valid_students.append(student)
                continue

            elif str(student['First name']) == "nan" and str(student['Last name']) == "nan" and str(student['Email']) == "nan":
                continue
            
            else:
                invalid_columns = ''
                if str(student['First name']) == "nan":
                    invalid_columns += 'First name'
                    logger.debug(
                        "Some columns were not filled properly : {}".format(invalid_columns))
                    raise HTTPException(
                        status_code=422, detail='We were not able to process the spreadsheet. Check that you have filled the '+invalid_columns+' column and upload again.')

                if str(student['Last name']) == "nan":
                    invalid_columns = 'Last name'
                    logger.debug(
                        "Some columns were not filled properly : {}".format(invalid_columns))
                    raise HTTPException(
                        status_code=422, detail='We were not able to process the spreadsheet. Check that you have filled the '+invalid_columns+' column and upload again.')

                if str(student['Email']) == "nan":
                    invalid_columns = 'Email'
                    logger.debug(
                        "Some columns were not filled properly : {}".format(invalid_columns))
                    raise HTTPException(
                        status_code=422, detail='We were not able to process the spreadsheet. Check that you have filled the '+invalid_columns+' column and upload again.')

                if self.validate_email(email = student['Email']) == False:
                    logger.debug("Invalid entry(s) found in email column : {}".format(
                        str(student['Email'])))
                    raise HTTPException(
                        status_code=422, detail='Invalid entries found in Email column')

                raise HTTPException(
                    status_code=422, detail='We were not able to process the spreadsheet. Check that you have filled all the columns and upload again.')
        
        return valid_students

    async def extract(self):
        self.validate_file()
        student_data = await self.extract_spreadsheet_data()

        if self.validate_columns(student_data = student_data):
            valid_data = self.validate_data(student_data = student_data)
            return valid_data

spreadsheet_util = SpreadsheetUtil()