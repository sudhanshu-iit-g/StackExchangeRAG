import os
import time
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.schema import StrOutputParser

from data_fetching import get_question_ids, fetch_and_process_answers

# Set up Google API key
os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY"

if __name__ == '__main__':
    search_query = input("Enter your initial math question (this will be used as the search query): ")
    total_results = 10
    site = 'math.stackexchange'
    question_ids = get_question_ids(search_query, total_results, site)
    print(f"Found {len(question_ids)} question IDs:")
    print(question_ids)
    doc = fetch_and_process_answers(question_ids)
    embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
    docs = [Document(page_content=answer) for answer in doc]
    vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.2)
    template = """You are a math expert answering questions based on information from Math Stack Exchange. Use the following context to answer the question at the end.
    Do not mention Stack Exchange or any external sources in your answer. Present the information as if it's your own expert knowledge.
    Be precise, clear, and helpful in your explanations. Try to give mathematical expression wherever possible.
    {context}
    Question: {question}
    Answer: """
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    rag_prompt_custom = ChatPromptTemplate.from_template(template)
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | rag_prompt_custom
        | llm
        | StrOutputParser()
    )
    summary_prompt = 'Summarize the key mathematical concepts discussed so far: '
    chathistory = [summary_prompt]

    output = rag_chain.invoke(search_query)
    print("\nAnswer to initial question:", output)
    print("\n" + "-"*50 + "\n")
    chathistory.append(search_query)

    while True:
        msg = input("Ask another math question (or type 'exit' to quit): ")
        if msg.lower() == 'exit':
            break
        time.sleep(1)
        all_previous_messages_with_prompt = ' '.join(chathistory)
        summary = rag_chain.invoke(all_previous_messages_with_prompt)
        final_chat_summary = f"Previous discussion summary: {summary}\n"
        to_ask = final_chat_summary + "New question: " + msg
        output = rag_chain.invoke(to_ask)
        chathistory.append(msg)
        print("\nAnswer:", output)
        print("\n" + "-"*50 + "\n")
    print("Thank you for using the Math Q&A system!")