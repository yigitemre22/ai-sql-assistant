#synchronize customer city names with city ids
#this pipeline looks up each customer's city
#in the cities table and fills customers.city_id

import unicodedata

from sqlalchemy import create_engine,select,update
from sqlalchemy.engine import URL

from app.config import settings
from app.models.database import Customer,City

#create the postgresql connection url safely
DATABASE_URL=URL.create(
    drivername="postgresql+psycopg2",
    username=settings.ingest_db_user,
    password=settings.ingest_db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name
)

#create the database engine
engine =create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

def normalize_city_name(city_name:str)->str:
    """
    normalize city names for reliable matching.

    example:
        Istanbul->istanbul,
        İstanbul->istanbul,
        Izmir->izmir,
        İzmir->izmir,
    """

    #convert to lowercase
    city_name=city_name.casefold()

    #normalized unicode charactes 
    city_name=unicodedata.normalize(
        "NFKD",
        city_name
    )

    #remove accent/combining marks
    city_name="".join(
        character
        for character in city_name
        if not unicodedata.combining(character)
    )

    #normalize turkish dotless i
    city_name=city_name.replace("ı","i")

    #remove surronding spaces
    return city_name.strip()

def sync_customer_cities()->None:
    """match customers with cities and update city_id"""

    with engine.begin() as connection:
        #read all cities from dimension table
        city_rows=connection.execute(
            select(
                City.id,
                City.name
            )
        ).all()

        #build a normalized city lookup dictionary
        city_lookup={
            normalize_city_name(name):city_id
            for city_id,name in city_rows
        }

        #read customers and their current city names
        customer_rows=connection.execute(
            select(
                Customer.id,
                Customer.city
            )
        ).all()

        updated_count=0

        for customer_id,city_name in customer_rows:
            #customer does not have a city
            if city_name is None:
                continue

            #normalize the customer's city
            normalized_city=normalize_city_name(
                city_name
            )

            #find the matching city id
            city_id=city_lookup.get(
                normalized_city
            )

            #stop the pipeline if the city cannot be matched
            if city_id is None:
                raise ValueError(
                    f"City '{city_name}'"
                    f"for customer {customer_id}"
                    f"could not be matched"
                )

            #update the foreign key
            connection.execute(
                update(Customer)
                .where(Customer.id==customer_id)
                .values(city_id=city_id)
            )

            updated_count+=1

    print(
        f"updated {updated_count} customer city relationships"
    )

def main()->None:
    """run the customer-city syncronization pipeline"""

    print("="*50)
    print("customer city sync pipeline")
    print("="*50)

    sync_customer_cities()

    print(
        "customer city synchronization completed successfully"
    )

if __name__=="__main__":
    main()