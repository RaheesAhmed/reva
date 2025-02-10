Supabase (Postgres)
Supabase is an open-source Firebase alternative. Supabase is built on top of PostgreSQL, which offers strong SQL querying capabilities and enables a simple interface with already-existing tools and frameworks.

PostgreSQL also known as Postgres, is a free and open-source relational database management system (RDBMS) emphasizing extensibility and SQL compliance.

Supabase provides an open-source toolkit for developing AI applications using Postgres and pgvector. Use the Supabase client libraries to store, index, and query your vector embeddings at scale.

In the notebook, we'll demo the SelfQueryRetriever wrapped around a Supabase vector store.

Specifically, we will:

Create a Supabase database
Enable the pgvector extension
Create a documents table and match_documents function that will be used by SupabaseVectorStore
Load sample documents into the vector store (database table)
Build and test a self-querying retriever
Setup Supabase Database
Head over to https://database.new to provision your Supabase database.
In the studio, jump to the SQL editor and run the following script to enable pgvector and setup your database as a vector store:
-- Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- Create a table to store your documents
create table
  documents (
    id uuid primary key,
    content text, -- corresponds to Document.pageContent
    metadata jsonb, -- corresponds to Document.metadata
    embedding vector (1536) -- 1536 works for OpenAI embeddings, change if needed
  );

-- Create a function to search for documents
create function match_documents (
  query_embedding vector (1536),
  filter jsonb default '{}'
) returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
) language plpgsql as $$
#variable_conflict use_column
begin
  return query
  select
    id,
    content,
    metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where metadata @> filter
  order by documents.embedding <=> query_embedding;
end;
$$;

Creating a Supabase vector store
Next we'll want to create a Supabase vector store and seed it with some data. We've created a small demo set of documents that contain summaries of movies.

Be sure to install the latest version of langchain with openai support:

%pip install --upgrade --quiet  langchain langchain-openai tiktoken

The self-query retriever requires you to have lark installed:

%pip install --upgrade --quiet  lark

We also need the supabase package:

%pip install --upgrade --quiet  supabase

Since we are using SupabaseVectorStore and OpenAIEmbeddings, we have to load their API keys.

To find your SUPABASE_URL and SUPABASE_SERVICE_KEY, head to your Supabase project's API settings.

SUPABASE_URL corresponds to the Project URL
SUPABASE_SERVICE_KEY corresponds to the service_role API key
To get your OPENAI_API_KEY, navigate to API keys on your OpenAI account and create a new secret key.

import getpass
import os

if "SUPABASE_URL" not in os.environ:
    os.environ["SUPABASE_URL"] = getpass.getpass("Supabase URL:")
if "SUPABASE_SERVICE_KEY" not in os.environ:
    os.environ["SUPABASE_SERVICE_KEY"] = getpass.getpass("Supabase Service Key:")
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")

Optional: If you're storing your Supabase and OpenAI API keys in a .env file, you can load them with dotenv.

%pip install --upgrade --quiet  python-dotenv

from dotenv import load_dotenv

load_dotenv()

First we'll create a Supabase client and instantiate a OpenAI embeddings class.

import os

from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from supabase.client import Client, create_client

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

embeddings = OpenAIEmbeddings()

API Reference:SupabaseVectorStore | Document | OpenAIEmbeddings
Next let's create our documents.

docs = [
    Document(
        page_content="A bunch of scientists bring back dinosaurs and mayhem breaks loose",
        metadata={"year": 1993, "rating": 7.7, "genre": "science fiction"},
    ),
    Document(
        page_content="Leo DiCaprio gets lost in a dream within a dream within a dream within a ...",
        metadata={"year": 2010, "director": "Christopher Nolan", "rating": 8.2},
    ),
    Document(
        page_content="A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea",
        metadata={"year": 2006, "director": "Satoshi Kon", "rating": 8.6},
    ),
    Document(
        page_content="A bunch of normal-sized women are supremely wholesome and some men pine after them",
        metadata={"year": 2019, "director": "Greta Gerwig", "rating": 8.3},
    ),
    Document(
        page_content="Toys come alive and have a blast doing so",
        metadata={"year": 1995, "genre": "animated"},
    ),
    Document(
        page_content="Three men walk into the Zone, three men walk out of the Zone",
        metadata={
            "year": 1979,
            "director": "Andrei Tarkovsky",
            "genre": "science fiction",
            "rating": 9.9,
        },
    ),
]

vectorstore = SupabaseVectorStore.from_documents(
    docs,
    embeddings,
    client=supabase,
    table_name="documents",
    query_name="match_documents",
)


Creating our self-querying retriever
Now we can instantiate our retriever. To do this we'll need to provide some information upfront about the metadata fields that our documents support and a short description of the document contents.

from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_openai import OpenAI

metadata_field_info = [
    AttributeInfo(
        name="genre",
        description="The genre of the movie",
        type="string or list[string]",
    ),
    AttributeInfo(
        name="year",
        description="The year the movie was released",
        type="integer",
    ),
    AttributeInfo(
        name="director",
        description="The name of the movie director",
        type="string",
    ),
    AttributeInfo(
        name="rating", description="A 1-10 rating for the movie", type="float"
    ),
]
document_content_description = "Brief summary of a movie"
llm = OpenAI(temperature=0)
retriever = SelfQueryRetriever.from_llm(
    llm, vectorstore, document_content_description, metadata_field_info, verbose=True
)

API Reference:AttributeInfo | SelfQueryRetriever | OpenAI
Testing it out
And now we can try actually using our retriever!

# This example only specifies a relevant query
retriever.invoke("What are some movies about dinosaurs")

query='dinosaur' filter=None limit=None

[Document(page_content='A bunch of scientists bring back dinosaurs and mayhem breaks loose', metadata={'year': 1993, 'genre': 'science fiction', 'rating': 7.7}),
 Document(page_content='Toys come alive and have a blast doing so', metadata={'year': 1995, 'genre': 'animated'}),
 Document(page_content='Three men walk into the Zone, three men walk out of the Zone', metadata={'year': 1979, 'genre': 'science fiction', 'rating': 9.9, 'director': 'Andrei Tarkovsky'}),
 Document(page_content='A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea', metadata={'year': 2006, 'rating': 8.6, 'director': 'Satoshi Kon'})]


# This example only specifies a filter
retriever.invoke("I want to watch a movie rated higher than 8.5")

query=' ' filter=Comparison(comparator=<Comparator.GT: 'gt'>, attribute='rating', value=8.5) limit=None

[Document(page_content='Three men walk into the Zone, three men walk out of the Zone', metadata={'year': 1979, 'genre': 'science fiction', 'rating': 9.9, 'director': 'Andrei Tarkovsky'}),
 Document(page_content='A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea', metadata={'year': 2006, 'rating': 8.6, 'director': 'Satoshi Kon'})]


# This example specifies a query and a filter
retriever.invoke("Has Greta Gerwig directed any movies about women?")

query='women' filter=Comparison(comparator=<Comparator.EQ: 'eq'>, attribute='director', value='Greta Gerwig') limit=None


[Document(page_content='A bunch of normal-sized women are supremely wholesome and some men pine after them', metadata={'year': 2019, 'rating': 8.3, 'director': 'Greta Gerwig'})]


# This example specifies a composite filter
retriever.invoke("What's a highly rated (above 8.5) science fiction film?")

query=' ' filter=Operation(operator=<Operator.AND: 'and'>, arguments=[Comparison(comparator=<Comparator.GTE: 'gte'>, attribute='rating', value=8.5), Comparison(comparator=<Comparator.EQ: 'eq'>, attribute='genre', value='science fiction')]) limit=None


[Document(page_content='Three men walk into the Zone, three men walk out of the Zone', metadata={'year': 1979, 'genre': 'science fiction', 'rating': 9.9, 'director': 'Andrei Tarkovsky'})]


# This example specifies a query and composite filter
retriever.invoke(
    "What's a movie after 1990 but before (or on) 2005 that's all about toys, and preferably is animated"
)


query='toys' filter=Operation(operator=<Operator.AND: 'and'>, arguments=[Comparison(comparator=<Comparator.GT: 'gt'>, attribute='year', value=1990), Comparison(comparator=<Comparator.LTE: 'lte'>, attribute='year', value=2005), Comparison(comparator=<Comparator.LIKE: 'like'>, attribute='genre', value='animated')]) limit=None


[Document(page_content='Toys come alive and have a blast doing so', metadata={'year': 1995, 'genre': 'animated'})]


Filter k
We can also use the self query retriever to specify k: the number of documents to fetch.

We can do this by passing enable_limit=True to the constructor.

retriever = SelfQueryRetriever.from_llm(
    llm,
    vectorstore,
    document_content_description,
    metadata_field_info,
    enable_limit=True,
    verbose=True,
)

# This example only specifies a relevant query
retriever.invoke("what are two movies about dinosaurs")

query='dinosaur' filter=None limit=2

[Document(page_content='A bunch of scientists bring back dinosaurs and mayhem breaks loose', metadata={'year': 1993, 'genre': 'science fiction', 'rating': 7.7}),
 Document(page_content='Toys come alive and have a blast doing so', metadata={'year': 1995, 'genre': 'animated'})]



Retriever options
This section goes over different options for how to use SupabaseVectorStore as a retriever.

Maximal Marginal Relevance Searches
In addition to using similarity search in the retriever object, you can also use mmr.

retriever = vector_store.as_retriever(search_type="mmr")

matched_docs = retriever.invoke(query)

for i, d in enumerate(matched_docs):
    print(f"\n## Document {i}\n")
    print(d.page_content)




We want to use OpenAIEmbeddings so we have to get the OpenAI API Key.

import getpass
import os

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")

if "SUPABASE_URL" not in os.environ:
    os.environ["SUPABASE_URL"] = getpass.getpass("Supabase URL:")

if "SUPABASE_SERVICE_KEY" not in os.environ:
    os.environ["SUPABASE_SERVICE_KEY"] = getpass.getpass("Supabase Service Key:")

# If you're storing your Supabase and OpenAI API keys in a .env file, you can load them with dotenv
from dotenv import load_dotenv

load_dotenv()

First we'll create a Supabase client and instantiate a OpenAI embeddings class.

import os

from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from supabase.client import Client, create_client

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

embeddings = OpenAIEmbeddings()

API Reference:SupabaseVectorStore | OpenAIEmbeddings
Next we'll load and parse some data for our vector store (skip if you already have documents with embeddings stored in your DB).

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

loader = TextLoader("../../how_to/state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

API Reference:TextLoader | CharacterTextSplitter
Insert the above documents into the database. Embeddings will automatically be generated for each document. You can adjust the chunk_size based on the amount of documents you have. The default is 500 but lowering it may be necessary.

vector_store = SupabaseVectorStore.from_documents(
    docs,
    embeddings,
    client=supabase,
    table_name="documents",
    query_name="match_documents",
    chunk_size=500,
)

Alternatively if you already have documents with embeddings in your database, simply instantiate a new SupabaseVectorStore directly:

vector_store = SupabaseVectorStore(
    embedding=embeddings,
    client=supabase,
    table_name="documents",
    query_name="match_documents",
)

Finally, test it out by performing a similarity search:

query = "What did the president say about Ketanji Brown Jackson"
matched_docs = vector_store.similarity_search(query)

print(matched_docs[0].page_content)

Tonight. I call on the Senate to: Pass the Freedom to Vote Act. Pass the John Lewis Voting Rights Act. And while you’re at it, pass the Disclose Act so Americans can know who is funding our elections. 

Tonight, I’d like to honor someone who has dedicated his life to serve this country: Justice Stephen Breyer—an Army veteran, Constitutional scholar, and retiring Justice of the United States Supreme Court. Justice Breyer, thank you for your service. 

One of the most serious constitutional responsibilities a President has is nominating someone to serve on the United States Supreme Court. 

And I did that 4 days ago, when I nominated Circuit Court of Appeals Judge Ketanji Brown Jackson. One of our nation’s top legal minds, who will continue Justice Breyer’s legacy of excellence.


Similarity search with score
The returned distance score is cosine distance. Therefore, a lower score is better.

matched_docs = vector_store.similarity_search_with_relevance_scores(query)

matched_docs[0]

(Document(page_content='Tonight. I call on the Senate to: Pass the Freedom to Vote Act. Pass the John Lewis Voting Rights Act. And while you’re at it, pass the Disclose Act so Americans can know who is funding our elections. \n\nTonight, I’d like to honor someone who has dedicated his life to serve this country: Justice Stephen Breyer—an Army veteran, Constitutional scholar, and retiring Justice of the United States Supreme Court. Justice Breyer, thank you for your service. \n\nOne of the most serious constitutional responsibilities a President has is nominating someone to serve on the United States Supreme Court. \n\nAnd I did that 4 days ago, when I nominated Circuit Court of Appeals Judge Ketanji Brown Jackson. One of our nation’s top legal minds, who will continue Justice Breyer’s legacy of excellence.', metadata={'source': '../../../state_of_the_union.txt'}),
 0.802509746274066)


Retriever options
This section goes over different options for how to use SupabaseVectorStore as a retriever.

Maximal Marginal Relevance Searches
In addition to using similarity search in the retriever object, you can also use mmr.

retriever = vector_store.as_retriever(search_type="mmr")

matched_docs = retriever.invoke(query)

for i, d in enumerate(matched_docs):
    print(f"\n## Document {i}\n")
    print(d.page_content)

